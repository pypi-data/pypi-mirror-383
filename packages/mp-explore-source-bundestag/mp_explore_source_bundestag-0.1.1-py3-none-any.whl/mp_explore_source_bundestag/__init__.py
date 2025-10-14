# SPDX-FileCopyrightText: 2025 Free Software Foundation Europe e.V. <mp-explore@fsfe.org>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from mp_explore_core import DataSource, ModuleDefinition, ModuleMaintainer, ModuleArgument, ModuleDescription
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import pandas as pd

import urllib.request
import urllib.parse
import subprocess
import logging
import unicodedata
import json
import re

class BundestagSource(DataSource):
    def __init__(self, display_browser: bool = False, skip_retired: bool = True, url: str = "https://www.bundestag.de/abgeordnete", infer_email: bool = False, check_cdu_csu: bool = False, cdu_csu_url: str = "https://www.cducsu.de/abgeordnete", check_grune: bool = False, grune_url: str = "https://www.gruene-bundestag.de/abgeordnete/", check_linke: bool = False, linke_url: str = "https://www.dielinkebt.de/abgeordnete/", check_spd: bool = False, spd_url: str = "https://www.spdfraktion.de/abgeordnete/alle"):
        """
        Retrieve the information of members from the Bundestag (German parliament)

        :param bool display_browser: (Display browser) When enabled, a browser window is opened displaying the actions being performed.
        :param bool skip_retired: (Skip retired members) Skip members who are retired, deceased, or refused mandate.
        :param str url: (URL) URL from where the data is extracted.
        :param bool infer_email: (Infer e-mail) When enabled, e-mails are inferred based on the pattern they typically follow.
        :param bool check_cdu_csu: (Check CDU/CSU) Obtain e-mails and check information with CDU/CSU sources.
        :param str cdu_csu_url: (CDU/CSU URL) The URL where the data will be extracted from.
        :param bool check_grune: (Check Grüne) Obtain e-mails and check information with Bündnis 90/Die Grünen sources.
        :param str grune_url: (Grüne URL) The URL where the data will be extracted from.
        :param bool check_linke: (Check Linke) Obtain e-mails and check information with Die Linke sources.
        :param str linke_url: (Linke URL) The URL where the data will be extracted from.
        :param bool check_spd: (Check SPD) Obtain e-mails and check information with SPD sources.
        :param str spd_url: (SPD URL) The URL where the data will be extracted from.
        """
        self.display_browser = display_browser
        self.skip_retired = skip_retired
        self.url = url
        self.infer_email = infer_email
        self.check_cdu_csu = check_cdu_csu
        self.cdu_csu_url = cdu_csu_url
        self.check_grune = check_grune
        self.grune_url = grune_url
        self.check_linke = check_linke
        self.linke_url = linke_url
        self.check_spd = check_spd
        self.spd_url = spd_url

    @staticmethod
    def metadata() -> ModuleDefinition:
        return ModuleDefinition({
            "name": "Bundestag",
            "identifier": "bundestag",
            "description": ModuleDescription.from_init(BundestagSource.__init__),
            "arguments": ModuleArgument.list_from_init(BundestagSource.__init__),
            "maintainers": [
                ModuleMaintainer({
                    "name": "Free Software Foundation Europe",
                    "email": "mp-explore@fsfe.org"
                }),
                ModuleMaintainer({
                    "name": "Sofía Aritz",
                    "email": "sofiaritz@fsfe.org"
                }),
            ],
        })

    def identifier(self) -> str:
        return "fsfe:bundestag"
    
    def _extract_title_and_name(self, val: str) -> (str, str):
        name_parts = val.split(" ")
        title = " ".join([x for x in name_parts if x.strip().endswith(".") and len(x.strip()) > 2])
        name = " ".join([x for x in name_parts if not x.strip().endswith(".") or len(x.strip()) <= 2])

        return (title, name)
    
    def _guess_email(self, name, surname):
        if "von" in name or "von" in surname:
            return None
        
        special_characters = {
            ord("ä"): "ae",
            ord("ü"): "ue",
            ord("ö"): "oe",
            ord("ß"): "ss",
            ord("ć"): "c",
        }

        name = name.translate(special_characters)
        surname = surname.translate(special_characters)

        name = name.replace(" ", "-")
        surname = surname.replace(" ", "-")

        norm_name = unicodedata.normalize("NFKD", name)
        norm_surname = unicodedata.normalize("NFKD", surname)

        name = ''.join([c for c in norm_name if not unicodedata.combining(c)])
        surname = ''.join([c for c in norm_surname if not unicodedata.combining(c)])

        return f"{name}.{surname}@bundestag.de".lower()
    
    async def fetch_data(self, logger: logging.Logger) -> pd.DataFrame:
        logger.warn("installing playwright browsers, if this fails try to run 'playwright install firefox --with-deps'")
        subprocess.run(["playwright", "install", "firefox"])

        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=self.display_browser is False)

            page = await browser.new_page()
            await page.goto(self.url)
            await page.wait_for_load_state()

            await page.locator(".bt-link-list").click()
            await page.wait_for_selector("ul.bt-list-holder")

            member_data = await page.evaluate("""() => {
                let elements = Array.from(document.getElementsByClassName("bt-teaser-person-text"))

                return elements.map((v) => {
                    let surname = v.children[0].innerText.split(",")[0].replace(/\(\w+\)/, "").trim();
                    let name = v.children[0].innerText.split(",")[1].trim();
                    let party = v.children[1].innerText.trim();

                    // Skip retired MPs
                    if ({{skip_retired}} && party.endsWith("*")) { return null }

                    return { surname, name, party }
                }).filter((v) => v != null);
            }""".replace("{{skip_retired}}", str(self.skip_retired).lower()))

            if self.check_spd:
                await page.goto(self.spd_url)
                await page.wait_for_load_state()

                spd_members = await page.evaluate("""() => {
                let cards = Array.from(document.querySelectorAll(".view-abgeordnete h3 a"))
                return cards.map((e) => {
                    let name = e.innerText
                    let url = e.href

                    return { name, url }
                })
                }""")

                spd_bundestag = [(index, item) for index, item in enumerate(member_data) if item["party"] == "SPD"]
                for i, bundestag_member in spd_bundestag:
                    for spd_member in spd_members:
                        bundestag_member_name = bundestag_member["name"] + " " + bundestag_member["surname"]
                        if bundestag_member_name in spd_member["name"]:
                            await page.goto(spd_member["url"])
                            await page.wait_for_load_state()

                            await page.wait_for_selector(".map_box_content")
                            email = await page.evaluate("""() => {
                                let links = Array.from(document.querySelectorAll(".map_box_content li a"))
                                return links.filter(e => e.href.startsWith("mailto:") && e.href.endsWith("@bundestag.de"))[0]?.href.replace("mailto:", "")
                            }""")

                            member_data[i]["email"] = email
                            await page.wait_for_timeout(150)

            if self.check_linke:
                await page.goto(self.linke_url)
                await page.wait_for_load_state()

                linke_members = await page.evaluate("""() => {
                let cards = Array.from(document.getElementsByClassName("frame-mdb-card"))
                return cards.map((e) => {
                    let name = e.getElementsByTagName("h2").item(0).innerText
                    let url = e.getElementsByTagName("a").item(0).href

                    return { name, url }
                })
                }""")

                linke_bundestag = [(index, item) for index, item in enumerate(member_data) if item["party"] == "Die Linke"]
                for i, bundestag_member in linke_bundestag:
                    for linke_member in linke_members:
                        bundestag_member_name = bundestag_member["name"] + " " + bundestag_member["surname"]
                        if bundestag_member_name in linke_member["name"]:
                            await page.goto(linke_member["url"])
                            await page.wait_for_load_state()

                            try:
                                await page.wait_for_selector(".mdb-email", timeout = 10000.0)
                            except PlaywrightTimeoutError:
                                # There's Linke members without published email
                                continue
                            email = await page.evaluate("""() => {
                                let links = Array.from(document.querySelectorAll(".mdb-email a"))
                                return links.filter(e => e.href.startsWith("mailto:"))[0]?.href.replace("mailto:", "")
                            }""")

                            member_data[i]["email"] = email
                            await page.wait_for_timeout(150)

            if self.check_grune:
                await page.goto(self.grune_url)
                await page.wait_for_load_state()

                grune_members = await page.evaluate("""() => {
                let cards = Array.from(document.getElementsByClassName("mp__card"))
                return cards.map((e) => {
                    let name = e.getElementsByClassName("mp__name").item(0).innerText
                    let url = e.getElementsByClassName("mp__link").item(0).href

                    return { name, url }
                })
                }""")

                grune_bundestag = [(index, item) for index, item in enumerate(member_data) if item["party"] == "Bündnis 90/Die Grünen"]
                for i, bundestag_member in grune_bundestag:
                    for grune_member in grune_members:
                        bundestag_member_name = bundestag_member["name"] + " " + bundestag_member["surname"]
                        if bundestag_member_name in grune_member["name"]:
                            await page.goto(grune_member["url"])
                            await page.wait_for_load_state()

                            await page.wait_for_selector(".mp-details__contact-box")
                            email = await page.evaluate("""() => {
                                let links = Array.from(document.getElementsByTagName("a"))
                                return links.filter(e => e.href.startsWith("mailto:") && e.href.endsWith("@bundestag.de"))[0]?.href.replace("mailto:", "")
                            }""")

                            member_data[i]["email"] = email
                            await page.wait_for_timeout(150)

            if self.check_cdu_csu:
                await page.goto(self.cdu_csu_url)
                await page.wait_for_load_state()

                await page.locator(".cn-decline").click()
                await page.wait_for_timeout(300)

                for x in range(100):
                    try:
                        await page.locator(".pager .pager__item .button").click(timeout=5000.0)
                        await page.wait_for_timeout(100)
                        await page.wait_for_selector(".pager .pager__item .button", timeout=5000.0)
                    except PlaywrightTimeoutError:
                        break

                cdu_csu_members = await page.evaluate("""() => {
                    let elements = Array.from(document.getElementsByClassName("views-field"))
                    return elements.map(e => {
                        let link = e.querySelector("a.text-lg")
                        let url = link.href
                        let name = link.innerText

                        return { url, name }
                    })
                }""")

                cdu_csu_bundestag = [(index, item) for index, item in enumerate(member_data) if item["party"] == "CDU/CSU"]
                for i, bundestag_member in cdu_csu_bundestag:
                    for cdu_csu_member in cdu_csu_members:
                        bundestag_member_name = bundestag_member["name"] + " " + bundestag_member["surname"]
                        if bundestag_member_name in cdu_csu_member["name"]:
                            await page.goto(cdu_csu_member["url"])
                            await page.wait_for_load_state()

                            await page.wait_for_selector(".paragraph--mdb-address")
                            email = await page.evaluate("""() => {
                                let info = document.querySelector(".paragraph--mdb-address a").innerText.split('\\n')[0].trim()
                                if (info.endsWith("@bundestag.de")) {
                                    return info
                                }
                                return ""
                            }""")

                            member_data[i]["email"] = email
                            await page.wait_for_timeout(150)

        members = []
        for member in member_data:
            title, name = self._extract_title_and_name(member["name"])
            member_dict = {
                "Title": title,
                "Surname": member["surname"],
                "Name": name,
                "Party": member["party"],
                "Email": member.get("email", None),
            }

            if self.infer_email is True and member_dict.get("Email") is None:
                member_dict["Email"] = self._guess_email(member_dict["Name"], member_dict["Surname"])
            
            members.append(member_dict)

        return pd.DataFrame(members)
