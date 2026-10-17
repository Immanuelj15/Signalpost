"""Tests for fact extraction engine and adapters."""

import pytest
from unittest.mock import patch, MagicMock
from signalpost.sources.brreg import BrregEnhetsregisterAdapter
from signalpost.sources.financial import BrregRegnskapAdapter
from signalpost.sources.website import CompanyWebsiteAdapter
from signalpost.models import VerificationStatus


@pytest.fixture
def mock_brreg_response():
    return {
        "organisasjonsnummer": "923609016",
        "navn": "EQUINOR ASA",
        "organisasjonsform": {
            "kode": "ASA",
            "beskrivelse": "Allmennaksjeselskap"
        },
        "registreringsdatoEnhetsregisteret": "2019-10-15",
        "stiftelsesdato": "1972-09-18",
        "antallAnsatte": 21000,
        "forretningsadresse": {
            "adresse": ["Forusbeen 50"],
            "postnummer": "4035",
            "poststed": "STAVANGER",
            "kommune": "STAVANGER",
            "kommunenummer": "1103",
            "land": "Norge",
            "landkode": "NO"
        },
        "naeringskode1": {
            "kode": "06.100",
            "beskrivelse": "Utvinning av råolje"
        },
        "aktivitet": ["Virksomhet knyttet til leting etter og utvinning av petroleum."],
        "hjemmeside": "www.equinor.com",
        "konkurs": False,
        "underAvvikling": False
    }


@pytest.fixture
def mock_regnskap_response():
    return [
        {
            "id": 5027445,
            "journalnr": "2024515327",
            "regnskapstype": "KONSERN",
            "regnskapsperiode": {
                "fraDato": "2023-01-01",
                "tilDato": "2023-12-31"
            },
            "valuta": "USD",
            "resultatregnskapResultat": {
                "aarsresultat": 11904000000.0,
                "ordinaertResultatFoerSkattekostnad": 37884000000.0,
                "driftsresultat": {
                    "driftsresultat": 35770000000.0,
                    "driftsinntekter": {
                        "salgsinntekter": 106848000000.0,
                        "sumDriftsinntekter": 107174000000.0
                    }
                }
            },
            "eiendeler": {
                "sumEiendeler": 143580000000.0
            },
            "egenkapitalGjeld": {
                "egenkapital": {
                    "sumEgenkapital": 48500000000.0
                },
                "gjeldOversikt": {
                    "sumGjeld": 95080000000.0
                }
            }
        }
    ]


def test_brreg_adapter_extraction(mock_brreg_response):
    adapter = BrregEnhetsregisterAdapter(cache_enabled=False)
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_brreg_response
    mock_resp.content = b'{"mock": true}'

    with patch.object(adapter, "safe_get", return_value=(mock_resp, None, 200)):
        facts, source_rec = adapter.fetch_and_extract("923609016")

    assert source_rec is not None
    assert source_rec.http_status == 200
    assert len(facts) >= 10

    fields = {f.field_name: f.value for f in facts}
    assert fields["official_name"] == "EQUINOR ASA"
    assert fields["organization_type"] == "ASA"
    assert fields["employees"] == 21000
    assert fields["website"] == "https://www.equinor.com"
    assert fields["status"] == "active"
    assert fields["is_in_bankruptcy"] is False


def test_regnskap_adapter_extraction(mock_regnskap_response):
    adapter = BrregRegnskapAdapter(cache_enabled=False)
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_regnskap_response
    mock_resp.content = b'{"mock": true}'

    with patch.object(adapter, "safe_get", return_value=(mock_resp, None, 200)):
        stmts, facts, source_rec = adapter.fetch_and_extract_statements("923609016")

    assert len(stmts) == 1
    stmt = stmts[0]
    assert stmt.year == 2023
    assert stmt.currency == "USD"
    assert stmt.total_revenue == 107174000000.0
    assert stmt.operating_profit == 35770000000.0
    assert stmt.net_profit == 11904000000.0
    assert stmt.total_assets == 143580000000.0
    assert stmt.total_equity == 48500000000.0
    assert stmt.total_debt == 95080000000.0

    # Verify atomic fact attribution
    rev_fact = next(f for f in facts if f.field_name == "total_revenue_2023")
    assert rev_fact.value == 107174000000.0
    assert rev_fact.reporting_period == "2023-01-01 to 2023-12-31"
    assert "brreg.no" in rev_fact.source_url


def test_website_adapter_extraction():
    adapter = CompanyWebsiteAdapter(cache_enabled=False)
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nordic Solutions AS</title>
        <meta name="description" content="Leading provider of sustainable subsea engineering solutions in Norway.">
    </head>
    <body>
        <p>Org.nr: 923609016</p>
        <p>Contact us at contact@nordicsolutions.no or call +47 22 33 44 55.</p>
        <h2>Våre Produkter og Tjenester</h2>
        <ul>
            <li>Subsea Pipeline Inspection</li>
            <li>Marine Seismic Monitoring</li>
        </ul>
    </body>
    </html>
    """

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = html_content

    with patch("signalpost.sources.website.is_safe_url", return_value=(True, None)):
        with patch.object(adapter, "safe_get", return_value=(mock_resp, None, 200)):
            facts, src_rec, meta = adapter.fetch_website_facts(
                org_nr="923609016",
                website_url="https://nordicsolutions.no",
                company_name="Nordic Solutions AS",
            )

    fields = {f.field_name: f.value for f in facts}
    assert "Leading provider" in fields["business_description"]
    assert fields["contact_email"] == "contact@nordicsolutions.no"
    assert "22334455" in fields["contact_phone"]
    assert "Subsea Pipeline Inspection" in fields["products_and_services"]
