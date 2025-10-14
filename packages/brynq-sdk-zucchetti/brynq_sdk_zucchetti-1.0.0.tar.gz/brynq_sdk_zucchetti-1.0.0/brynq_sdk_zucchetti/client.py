from dataclasses import dataclass
from requests import Session
from requests.adapters import HTTPAdapter, Retry
from zeep import Client, Settings
from zeep.plugins import HistoryPlugin
from zeep.transports import Transport
from lxml import etree

@dataclass
class ZucchettiConfig:
    wsdl_link: str
    username: str
    password: str
    company: str
    timeout: int = 60

class ZucchettiClient:
    """
    SOAP client for Zucchetti hrut_brecvinsertrec_Run using zeep.
    """

    def __init__(self, cfg: ZucchettiConfig):
        self.cfg = cfg

        # Robust HTTP session with retries
        session = Session()
        retries = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("POST", "GET"),
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        self.history = HistoryPlugin()
        self.client = Client(
            wsdl=cfg.wsdl_link,
            transport=Transport(session=session, timeout=cfg.timeout),
            settings=Settings(strict=False, xml_huge_tree=True),
            plugins=[self.history],
        )


    def run_import(self, pfile: str) -> str:
        """
        Call hrut_brecvinsertrec_Run operation.
        Note: If the service *requires* CDATA specifically, see approach 2 below.
        """
        # Use the standard zeep service call
        try:
            resp = self.client.service.hrut_brecvinsertrec_Run(
                m_UserName=self.cfg.username,
                m_Password=self.cfg.password,
                m_Company=self.cfg.company,
                pFILE=pfile,
            )

            resp_xml = self.last_request_response_xml()
            return resp, resp_xml
        except Exception as e:
            raise ValueError(f"Service call failed: {e}") from e


    def last_request_response_xml(self) -> str:
        """
        Inspect last SOAP exchange (helpful for troubleshooting).
        """
        req = self.history.last_sent["envelope"] if self.history.last_sent else None
        res = self.history.last_received["envelope"] if self.history.last_received else None
        req = etree.tostring(req, pretty_print=True, encoding='unicode')
        res = etree.tostring(res, pretty_print=True, encoding='unicode')
        return res
