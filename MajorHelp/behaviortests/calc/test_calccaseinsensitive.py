# Generated by Selenium IDE
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class TestCalccaseinsensitive():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_calccaseinsensitive(self):
    self.driver.get("http://127.0.0.1:8000/")
    self.driver.find_element(By.LINK_TEXT, "Tuition Calculator").click()
    self.driver.find_element(By.ID, "uni").click()
    self.driver.find_element(By.ID, "uni").send_keys("CLEMSON")
    self.driver.find_element(By.ID, "dept").click()
    dropdown = self.driver.find_element(By.ID, "dept")
    dropdown.find_element(By.XPATH, "//option[. = 'Engineering and Technology']").click()
    self.driver.find_element(By.CSS_SELECTOR, "option:nth-child(6)").click()
    self.driver.find_element(By.ID, "major").click()
    self.driver.find_element(By.ID, "major").send_keys("CIS")
    self.driver.find_element(By.ID, "aid").click()
    self.driver.find_element(By.ID, "aid").send_keys("PALMETTO FELLOWS")
    self.driver.find_element(By.ID, "submitButton").click()
    elements = self.driver.find_elements(By.ID, "output")
    assert len(elements) > 0
  
