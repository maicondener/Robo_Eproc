import pytest
from unittest.mock import AsyncMock, patch
from src.scripts.base import BaseScraper, ScraperResult
from playwright.async_api import Page

class DummyScraper(BaseScraper):
    async def run(self, page: Page) -> ScraperResult:
        return ScraperResult(success=True, message="Dummy OK")

@pytest.fixture
def dummy_scraper():
    return DummyScraper()

@pytest.mark.asyncio
async def test_base_scraper_run(dummy_scraper):
    page_mock = AsyncMock(spec=Page)
    result = await dummy_scraper.run(page_mock)
    
    assert result.success is True
    assert result.message == "Dummy OK"

@pytest.mark.asyncio
async def test_wait_and_fill(dummy_scraper):
    page_mock = AsyncMock(spec=Page)
    
    await dummy_scraper.wait_and_fill(page_mock, "#teste", "valor")
    
    page_mock.wait_for_selector.assert_called_once_with("#teste", timeout=5000)
    page_mock.fill.assert_called_once_with("#teste", "valor")

@pytest.mark.asyncio
async def test_wait_and_click(dummy_scraper):
    page_mock = AsyncMock(spec=Page)
    
    await dummy_scraper.wait_and_click(page_mock, "#btn")
    
    page_mock.wait_for_selector.assert_called_once_with("#btn", timeout=5000)
    page_mock.click.assert_called_once_with("#btn")
