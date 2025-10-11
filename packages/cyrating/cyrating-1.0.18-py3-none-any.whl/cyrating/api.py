# -*- coding: utf-8 -*-

import requests
from requests.adapters import HTTPAdapter
import configparser
import jwt
import json
import sys
from datetime import datetime


PATH_MASTER_TOKEN = "./cyrating.ini"
APP_URL = "https://api.cyrating.com"
COMPANY_ENDPOINT = "/company"
CLIENT_ENDPOINT = "/client"
CERTIFICATE_ENDPOINT = "/manage_report"
ASSETS_ENDPOINT = "/assets"
ELEMENTS_ENDPOINT = "/elements"
TAGS_ENDPOINT = "/tags"
EVENTS_ENDPOINT = "/events"
FACTS_ENDPOINT = "/facts"
ASSESSMENT_ENDPOINT = "/assessment"
CHRONICLE_RATING_ENDPOINT = "/chronicle/rating"
CHRONICLE_DOMAIN_ENDPOINT = "/chronicle/domain"
CHRONICLE_DEDICATED_SUB_ENDPOINT = "/chronicle/dedicated_sub"
TECHNOLOGIES_ENDPOINT = "/technology"
SCOPE_UPDATES_ENDPOINT = "/scope/updates"

event_categories = dict(
    SP="Spam propagation",
    IC="Involvement in cyberattacks",
    BR="Bad reputation",
    HM="Hosting malicious services",
)

names = {
    "rdp": "RDP",
    "smb": "SMB",
    "netbios": "Netbios",
    "mongodb": "MongoDB",
    "couchdb": "CouchDB",
    "elasticsearch": "ElasticSearch",
    "zookeeper": "ZooKeeper",
    "mysql": "MySQL",
    "redis": "Redis",
    "cassandra": "Cassandra",
    "kafka": "Kafka",
    "mssql": "Microsoft SQL",
    "postgresql": "PostgreSQL",
}


def jsonFilter(dic):
    if isinstance(dic, list):
        return dic
    res = {}
    for key in dic.keys():
        if not key.startswith("_"):
            res[key] = dic[key]
    return res


class Cyrating(object):
    def __init__(self, **kwargs):
        """Init a Cyrating context"""

        self.__access_token__ = (
            kwargs.get("token") if "token" in kwargs else self.get_personal_token()
        )
        self.__proxies__ = kwargs.get("proxies", None)
        decoded_atoken = jwt.decode(
            self.__access_token__,
            "secret",
            algorithms=["PS512"],
            options={"verify_signature": False},
        )
        self._requests = requests.Session()
        self._requests.mount("", HTTPAdapter(max_retries=5))
        self.__app_url__ = "http://127.0.0.1:5000" if kwargs.get("debug") else APP_URL
        self.__headers__ = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.__access_token__,
        }
        self.__current_user_id__ = decoded_atoken["sub"]

        (tmp, self.__current_client_id__, self.__current_role) = decoded_atoken[
            "ccs"
        ].split(":")
        self.client(self.__current_client_id__)
        print(
            "# Access Token for",
            self.__app_url__,
            "expires at",
            datetime.fromtimestamp(decoded_atoken["exp"]),
            file=sys.stderr,
        )
        if self.__proxies__ is not None:
            self._requests.proxies = self.__proxies__

    def get_personal_token(self):
        """Read personal token from configuration file"""

        config = configparser.ConfigParser()
        config.read(PATH_MASTER_TOKEN)
        return config["cyrating"]["token"]

    def get(self, endpoint, id, extraHttpRequestParams=None):
        url = self.__app_url__ + endpoint + "/" + id
        res = self._requests.get(
            url, params=extraHttpRequestParams, headers=self.__headers__
        )
        if res.ok:
            jData = json.loads(res.content)
            return jData

        if res.status_code == 401:
            raise (Exception("Invalid token"))

        return None

    def post(self, endpoint, obj, extraHttpRequestParams=None):
        res = self._requests.post(
            self.__app_url__ + endpoint,
            json.dumps(obj),
            params=extraHttpRequestParams,
            headers=self.__headers__,
        )
        print(json.dumps(obj))
        print(res.text)
        print(res.url)
        if res.ok:
            jData = json.loads(res.content)
            return jData

    def patch(self, obj, extraHttpRequestParams=None):
        headers = self.__headers__.copy()
        headers.update({"If-Match": obj["_etag"]})

        res = self._requests.patch(
            self.__app_url__ + "/" + obj["_links"]["self"]["href"],
            json.dumps(jsonFilter(obj)),
            headers=headers,
            params=extraHttpRequestParams,
            stream=False,
        )

        if res.ok:
            jData = json.loads(res.content)
            return jData

        if res.status_code == 403:
            raise (Exception("You need an admin role to carry out this operation."))

        if res.status_code == 422:
            jData = json.loads(res.content)
            raise (Exception("Unprocessable Entity: {}".format(jData["_issues"])))

        if res.status_code == 401:
            raise (Exception("Invalid token"))

        return None

    def find_one(self, endpoint, extraHttpRequestParams=None):
        queryParameters = {"page": 1, "max_results": 100}

        if extraHttpRequestParams:
            queryParameters.update(extraHttpRequestParams)

        res = self._requests.get(
            self.__app_url__ + endpoint,
            params=queryParameters,
            headers=self.__headers__,
        )
        if res.ok:
            jData = json.loads(res.content)
            assert (
                len(jData["_items"]) >= 0
            ), "Error multiple instance of {} in {}".format(
                extraHttpRequestParams, endpoint
            )
            if len(jData["_items"]) == 0:
                return None
            return jData["_items"][0]

        if res.status_code == 401:
            print(res.content)
            raise (Exception("Invalid token"))

        return None

    def findall(self, endpoint, page=1, extraHttpRequestParams=None):
        queryParameters = {"page": page, "max_results": 100}

        if extraHttpRequestParams:
            queryParameters.update(extraHttpRequestParams)

        res = self._requests.get(
            self.__app_url__ + endpoint,
            params=queryParameters,
            headers=self.__headers__,
        )
        if res.ok:
            jData = json.loads(res.content)
            if len(jData["_items"]) != 0:
                to_append = self.findall(endpoint, page + 1, extraHttpRequestParams)
                jData["_items"].extend(to_append)

            return jData["_items"]

        if res.status_code == 401:
            raise (Exception("Invalid token"))

        return None

    def client(self, clientid):
        """Retrieve client obj from API"""
        answer = self.get(CLIENT_ENDPOINT, clientid)
        if not answer:
            self.__current_client__ = None
            return
        self.__current_client__ = dict(
            _id=answer.get("_id", None),
            name=answer.get("name", None),
            user=answer.get("user", None),
            company_id=answer.get("companyID", None),
            entities_id=answer.get("entitiesID", None),
            suppliers_id=answer.get("suppliersID", None),
            competitors_id=answer.get("competitorsID", None),
        )

    def get_company(self, id):
        """Retrieve company obj from API"""

        return self.get(COMPANY_ENDPOINT, id)

    def certificate(self, company, filename=None):
        """Get certificate of a company"""

        httpParams = dict(
            client=self.__current_client_id__,
            organization=company["_id"],
            certificate="true",
        )
        answer = self._requests.get(
            self.__app_url__ + CERTIFICATE_ENDPOINT,
            params=httpParams,
            headers=self.__headers__,
        )

        if not answer.ok:
            raise Exception(
                "Failed to retreive certificate for {}".format(company["name"])
            )

        if filename:
            try:
                with open(filename, "wb") as f:
                    f.write(answer.content)
            except Exception as e:
                raise Exception("Failed to save {}: {}".format(filename, e))
        else:
            return answer.content

    def main_company(self):
        """Get main company"""

        return self.get_company(self.__current_client__["company_id"])

    def entities(self):
        """Get list of entities"""

        return [
            self.get_company(companyid)
            for companyid in self.__current_client__["entities_id"]
        ]

    def suppliers(self):
        """Get list of suppliers"""

        return [
            self.get_company(companyid)
            for companyid in self.__current_client__["suppliers_id"]
        ]

    def competitors(self):
        """Get list of competitors"""

        return [
            self.get_company(companyid)
            for companyid in self.__current_client__["competitors_id"]
        ]

    def internal_get_elements(self, company):
        """Get list of elements of a company"""

        filter = {"where": json.dumps({"company": company["_id"]})}
        return self.find_one(ELEMENTS_ENDPOINT, filter)

    def internal_get_assets(self, company):
        """Get list of assets of a company"""

        filter = {"where": json.dumps({"company": company["_id"]})}
        return self.find_one(ASSETS_ENDPOINT, filter)

    def domains(self, company):
        elements = self.internal_get_elements(company)
        if elements is not None:
            return [
                item["name"]
                for item in elements["elements"]
                if item["type"] == "domain"
            ]
        return None

    def domains_deprecated(self, company):
        """Get list of domains associated to a company"""

        assets = self.internal_get_assets(company)

        if assets is not None:
            return [
                item["label"] for item in assets["nodes"] if item["type"] == "domain"
            ]
        return None

    def set_tags(self, name, tags):
        if name is None:
            print("* Domain name is None")
            return
        if not isinstance(tags, list):
            print("* Tags is not an array")
            return
        tags_obj = self.get(TAGS_ENDPOINT, name)

        if not tags_obj:
            raise (Exception("{} does not exist.".format(name)))
        tags_obj.update({"tags": tags})
        self.patch(tags_obj)

    def assets(self, company):
        f = {"where": json.dumps({"company": company["_id"]})}
        company_tags = self.findall(TAGS_ENDPOINT, 1, f)
        tags = dict()
        if company_tags:
            for item in company_tags:
                tags[item["name"]] = item["tags"] if "tags" in item else []

        elements = self.internal_get_elements(company)
        elements = [
            asset for asset in elements["elements"] if asset["type"] != "custom_ips"
        ]
        for element in elements:
            local_tags = set()
            for domain in element["domains"]:
                local_tags |= set(tags.get(domain, []))
            element["tags"] = list(local_tags)
        return elements

    def assets_deprecated(self, company):
        filter = {"where": json.dumps({"company": company["_id"]})}
        company_tags = self.findall(TAGS_ENDPOINT, 1, filter)
        tags = dict()
        domains_map = dict()

        enable_entities = False
        entities_map = dict()
        if company["_id"] == self.__current_client__["company_id"]:
            enable_entities = True
            companies_id = self.__current_client__["entities_id"] or []
            filter = {"where": json.dumps({"_id": {"$in": companies_id}})}
            entities = self.findall(COMPANY_ENDPOINT, 1, filter)
            filter = {"where": json.dumps({"company": {"$in": companies_id}})}
            entities_assets = self.findall(ASSETS_ENDPOINT, 1, filter)

            for entity in entities:
                assets = next(
                    assets
                    for assets in entities_assets
                    if assets["company"] == entity["_id"]
                )
                domains = [
                    node["label"]
                    for node in assets["nodes"]
                    if node["type"] == "domain"
                ]
                for domainname in domains:
                    if domainname not in entities_map:
                        entities_map[domainname] = []
                    entities_map[domainname].append(entity["name"])

        if company_tags:
            for item in company_tags:
                tags[item["name"]] = item["tags"] if "tags" in item else []
                domains_map[item["name"]] = item["name"]

        assets = self.internal_get_assets(company)
        domains = [
            node["label"]
            for node in assets["nodes"]
            if node["type"] in ["domain", "asn"]
        ]

        res = dict()
        for node in assets["nodes"]:
            if node["label"] in res and node["type"] not in ["domain", "asn"]:
                continue

            if node["label"] not in res:
                res[node["label"]] = {
                    "type": node["type"],
                    "tags": [],
                    "domains": [],
                    "entities": [],
                    "_updated": False,
                }

            if node["type"] in ["domain", "asn"]:
                res[node["label"]]["tags"] = list(
                    set(
                        res[node["label"]]["tags"] + tags[node["label"]]
                        if node["label"] in tags
                        else []
                    )
                )

                toadd = (
                    [domains_map[node["label"]]]
                    if node["label"] in domains_map
                    else [node["label"]]
                )
                res[node["label"]]["domains"] = list(
                    set(res[node["label"]]["domains"] + toadd)
                )
                res[node["label"]]["entities"] = (
                    entities_map[node["label"]]
                    if enable_entities and node["label"] in entities_map
                    else []
                )
                res[node["label"]]["_updated"] = True

        for link in assets["links"]:
            if link["source"] in domains:
                res[link["target"]]["tags"] = list(
                    set(res[link["source"]]["tags"] + res[link["target"]]["tags"])
                )
                res[link["target"]]["domains"] = list(
                    set(res[link["source"]]["domains"] + res[link["target"]]["domains"])
                )
                res[link["target"]]["entities"] = list(
                    set(
                        res[link["source"]]["entities"]
                        + res[link["target"]]["entities"]
                    )
                )
                res[link["target"]]["_updated"] = True

        for link in assets["links"]:
            if res[link["target"]]["_updated"] is False:
                res[link["target"]]["tags"] = list(
                    set(res[link["source"]]["tags"] + res[link["target"]]["tags"])
                )
                res[link["target"]]["domains"] = list(
                    set(res[link["source"]]["domains"] + res[link["target"]]["domains"])
                )
                res[link["target"]]["entities"] = list(
                    set(
                        res[link["source"]]["entities"]
                        + res[link["target"]]["entities"]
                    )
                )
                res[link["target"]]["_updated"] = True

        return res

    def technologies(self, company, assets=None):
        enrich = Cyrating.format_enrich(assets)
        f = {"where": json.dumps({"company": company["_id"]})}
        technologies = self.findall(TECHNOLOGIES_ENDPOINT, 1, f)

        res = []
        for tech in technologies:
            item = {
                "name": tech["name"],
                "category": tech["category"],
                "asset": tech["asset"],
                "tags": Cyrating.enrich_tags(enrich, tech["asset"]),
                "related": Cyrating.enrich_related(enrich, tech["asset"]),
                "entities": Cyrating.enrich_entities(enrich, tech["asset"]),
            }
            res.append(item)
        return res

    def events(self, company, assets=None):
        enrich = Cyrating.format_enrich(assets)
        filter = {"where": json.dumps({"company": company["_id"]})}
        events = self.find_one(EVENTS_ENDPOINT, filter)

        res = []
        for key in events["assessment"].keys():
            for event in events["assessment"][key]:
                for source in event["sources"]:
                    item = {
                        "name": event["name"],
                        "type": event["type"],
                        "occurrences": source["occurences"],
                        "category": event_categories[key],
                        "source": {
                            "tag": source["name"],
                            "url": source["url"] if "url" in source else None,
                        },
                        "impact": event["impact"],
                        "tags": Cyrating.enrich_tags(enrich, event["name"]),
                        "related": Cyrating.enrich_related(enrich, event["name"]),
                        "entities": Cyrating.enrich_entities(enrich, event["name"]),
                    }
                    res.append(item)

        return res

    def format_result(self, results):
        res = ""
        for result in results:
            if "label" in result:
                res += "{}{}".format(result["label"], ": " if "value" in result else "")
            if "value" in result:
                res += "{}".format(result["value"])
            res += "\r\n"
        return res.rstrip("\r\n")

    def format_result_us(self, us):
        res = "{} detected on port {}/{}".format(
            names.get(us["service"], us["service"]), str(us["port"]), us["proto"]
        )
        return res

    @staticmethod
    def enrich_tags(enrich, name):
        try:
            return enrich[name]["tags"]
        except Exception:
            return None

    @staticmethod
    def enrich_entities(enrich, name):
        try:
            return enrich[name]["entities"]
        except Exception:
            return None

    @staticmethod
    def enrich_related(enrich, name):
        try:
            return enrich[name]["related"]
        except Exception:
            return None

    @staticmethod
    def format_enrich(assets):
        if assets is None:
            return None
        enrich = dict()
        for item in assets:
            enrich[item["name"]] = dict(
                entities=item["entities"],
                related=item["related"],
                type=item["type"],
                tags=item["tags"],
            )
        return enrich

    def facts(self, company, assets=None, extra_filter=None):
        enrich = Cyrating.format_enrich(assets)
        where = {"companies": company["_id"]}
        if extra_filter is not None:
            where.update(extra_filter)
        f = {"where": json.dumps(where)}
        f.update({"max_results": 1000})
        assessements = self.findall(ASSESSMENT_ENDPOINT, 1, f)
        global_us = dict()

        factorize_exposed_admin_panel = dict()
        res = []
        for assessment in assessements:
            control = assessment["name"]
            category = assessment["kci"]
            if (
                control.startswith("HTTP")
                or control.startswith("SSL")
                or control.startswith("Web")
            ):
                for result in assessment["result"]:
                    try:
                        grade = result["subscore"] / result["subbaseline"]
                    except Exception:
                        grade = "N/A"
                    name = result["host"].replace("http://", "").replace("https://", "")
                    item = {
                        "domain": assessment["domainname"],
                        "tags": Cyrating.enrich_tags(enrich, name),
                        "entities": Cyrating.enrich_entities(enrich, name),
                        "related": Cyrating.enrich_related(enrich, name),
                        "control": control,
                        "category": category,
                        "name": result["host"],
                        "type": "host",
                        "grade": grade,
                        "results": "{}: {}".format(result["label"], result["value"]),
                    }
                    res.append(item)
                continue
            if category == "US":
                for us in assessment["result"] or []:
                    hostip = us.get("IPv4", us.get("host", None))
                    ports = str(us["port"])
                    key = hostip + "-" + ports + "/" + us["proto"]
                    if key in global_us:
                        if not isinstance(global_us[key]["domain"], list):
                            global_us[key]["domain"] = [global_us[key]["domain"]]
                        global_us[key]["domain"].append(assessment["domainname"])
                    else:
                        item = {
                            "domain": assessment["domainname"],
                            "tags": Cyrating.enrich_tags(enrich, hostip),
                            "entities": Cyrating.enrich_entities(enrich, hostip),
                            "related": Cyrating.enrich_related(enrich, hostip),
                            "category": category,
                            "control": control,
                            "name": hostip,
                            "type": "hostip",
                            "impact": us["impact"],
                            "results": self.format_result_us(us),
                        }
                        global_us[key] = item
                        res.append(item)
                continue
            if control in [
                "SubdomainsTakeover",
                "ExposedCredentials",
                "OrphanDNSRecords",
            ]:
                for result in assessment["result"]:
                    item = {
                        "domain": assessment["domainname"],
                        "tags": Cyrating.enrich_tags(enrich, result["host"]),
                        "entities": Cyrating.enrich_entities(enrich, result["host"]),
                        "related": Cyrating.enrich_related(enrich, result["host"]),
                        "control": control,
                        "category": category,
                        "name": result["host"],
                        "type": "host",
                        "impact": -1,
                        "results": "{}: {}".format(result["label"], result["value"]),
                    }
                    res.append(item)
                continue
            if control in ["ExposedAdminPanels"]:
                for result in assessment["result"]:
                    hostip = (
                        result["host"] if "host" in result.keys() else result["IPv4"]
                    )
                    key = hostip + "{}: {}".format(
                        result["label"], result["value"].split(" (found on")[0]
                    )
                    if key in factorize_exposed_admin_panel:
                        factorize_exposed_admin_panel[key]["impact"] -= 1
                        continue
                    item = {
                        "domain": assessment["domainname"],
                        "tags": Cyrating.enrich_tags(enrich, hostip),
                        "entities": Cyrating.enrich_entities(enrich, hostip),
                        "related": Cyrating.enrich_related(enrich, hostip),
                        "control": control,
                        "category": category,
                        "name": hostip,
                        "type": "hostip",
                        "impact": -1,
                        "results": "{}: {}".format(result["label"], result["value"]),
                    }
                    factorize_exposed_admin_panel[key] = item
                    res.append(item)
                continue

            try:
                grade = assessment["score"] / assessment["baseline"]
            except Exception:
                grade = "N/A"
            item = {
                "domain": assessment["domainname"],
                "tags": Cyrating.enrich_tags(enrich, assessment["domainname"]),
                "entities": Cyrating.enrich_entities(enrich, assessment["domainname"]),
                "related": Cyrating.enrich_related(enrich, assessment["domainname"]),
                "category": category,
                "control": control,
                "name": assessment["domainname"],
                "type": "domain",
                "grade": grade,
                "results": self.format_result(assessment["result"]),
            }
            res.append(item)
        return res

    def members(self):
        users = []
        for user in self.__current_client__["user"]:
            user["client"] = self.__current_client__["name"]
            user.pop("user")
            users.append(user)

        filter = {"where": json.dumps({"parent": self.__current_client__["_id"]})}
        childs = self.findall(CLIENT_ENDPOINT, 1, filter)
        for child in childs:
            for user in child["user"]:
                user["client"] = child["name"]
                user.pop("user")
                users.append(user)
        return users

    def rating_history(self, company):
        filter = {"where": json.dumps({"company": company["_id"]}), "sort": "-date"}
        filter.update({"max_results": 1000})
        ratings = self.findall(CHRONICLE_RATING_ENDPOINT, 1, filter)
        return ratings

    def scope(self, company):
        filter = {"where": json.dumps({"company": company["_id"]}), "sort": "-date"}
        filter.update({"max_results": 1000})
        ratings = self.findall(CHRONICLE_DOMAIN_ENDPOINT, 1, filter)
        return ratings

    def scope_trends(self, scope):
        res = []
        last_domains = None
        for item in scope:
            current_domains = set(item["domainnames"])
            if last_domains is not None:
                added_domains = current_domains - last_domains
                removed_domains = last_domains - current_domains
                if len(added_domains) > 0 or len(removed_domains) > 0:
                    res.append(
                        {
                            "date": item["_created"],
                            "added": list(added_domains),
                            "removed": list(removed_domains),
                        }
                    )
            last_domains = current_domains
        return res

    def get_mean(self, data, name, kpi):
        for item in data:
            if item["name"] == name:
                return item["spf"]["mean"]
        return None

    def global_analytics(self, company, kpi="spf"):
        f = {"where": json.dumps({"company": company["_id"]}), "sort": "-date"}
        f.update({"max_results": 2})
        ga = self.findall(
            CHRONICLE_DEDICATED_SUB_ENDPOINT + "_" + self.__current_client_id__, 1, f
        )
        if not ga or kpi not in ["spf", "composite_wp"]:
            return None

        current_date = ga[0]["date"]
        data = ga[0]["figures"]

        res = dict(current_date=current_date, kpi=kpi, data=[])
        for item in data:
            res["data"].append(
                {
                    "name": item["name"],
                    "mean": item[kpi]["mean"],
                    "score": item[kpi]["score"],
                    "count": item[kpi]["count"],
                    "trend": item[kpi]["mean"]
                    - self.get_mean(ga[1]["figures"], item["name"], kpi),
                }
            )
        return res

    def scope_updates(self, company):
        filter = {"where": json.dumps({"companies": {"$in": [company["_id"]]}})}
        filter.update({"max_results": 1000})
        scope_updates = self.findall(SCOPE_UPDATES_ENDPOINT, 1, filter)
        return scope_updates

    def manage_scope_updates(self, company, action, name, type=None, tags=None):
        if company is None:
            print("* Company is None")
            return
        if name is None:
            print("* Name is None")
            return
        if tags and not isinstance(tags, list):
            print("* Tags is not an array")
            return

        scope_updates_obj = self.get(SCOPE_UPDATES_ENDPOINT, name)

        if scope_updates_obj is None:
            scope_updates_obj = dict(name=name, is_new=True)

        scope_updates_obj.update(
            {
                "company": company["_id"],
                "action": action,
            }
        )
        if type is not None:
            scope_updates_obj.update({"type": type})
        if tags is not None:
            scope_updates_obj.update({"tags": tags})

        if scope_updates_obj.get("is_new", False):
            del scope_updates_obj["is_new"]
            self.post(SCOPE_UPDATES_ENDPOINT, scope_updates_obj)
        else:
            self.patch(scope_updates_obj)

    def add_asset(self, company, name, type, tags=None):
        return self.manage_scope_updates(company, "add", name, type, tags)

    def remove_asset(self, company, name, type):
        return self.manage_scope_updates(company, "remove", name, type)

    def cancel_update(self, company, name):
        return self.manage_scope_updates(company, "cancel", name)

    # legacy methods
    get_members = members
    get_rating_history = rating_history
    get_facts = facts
    get_events = events
    get_assets = assets_deprecated
    get_certificate = certificate
