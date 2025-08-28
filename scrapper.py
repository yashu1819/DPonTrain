import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
                                                                                                    
                                                                                                                                                                        
class IRCTCTrainBot:
    """
    A robust bot that uses container-based search logic to find and
    refresh train availability on the IRCTC website.
    """
                                                                                                        
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print("🤖 Browser session started.")

    def _select_station(self, input_selector, station_code, station_name):
        """Helper function to type and select a station from the dropdown."""
        station_input = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, input_selector))
        )
        
        station_input.clear()
        station_input.send_keys(station_code)

        dropdown_option_xpath = f"//li[@role='option' and contains(., '{station_name}') and contains(., '{station_code}')]"
        self.wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_option_xpath))).click()

    def check_availability(self, from_station, from_name, to_station, to_name, train_no, class_code, journey_date):
        """
        journey_date must be in 'dd/MM/yyyy' format (e.g., '27/08/2025').
        """
        try:
            print(f"\nStarting availability check for Train {train_no}...")
            self.driver.get("https://www.irctc.co.in/nget/train-search")
            self.wait = WebDriverWait(self.driver, 20)

            # 1. Handle Alert if present
            ok_button_xpath = "//button[contains(@class, 'btn-primary') and text()='OK']"
            try:
                ok_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, ok_button_xpath)))
                ok_button.click()
                print("✅ Alert closed.")
            except TimeoutException:
                print("ℹ No alert found, continuing...")

            # 2. Fill Station Details
            self._select_station("input[aria-controls='pr_id_1_list']", from_station, from_name)
            self._select_station("input[aria-controls='pr_id_2_list']", to_station, to_name)

            # 3. Enter Journey Date
            
            date_input = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[class='ng-tns-c59-10 ui-inputtext ui-widget ui-state-default ui-corner-all ng-star-inserted']"))
            )
            date_input.click()
            date_input.send_keys(Keys.CONTROL, "a")   # Select all
            date_input.send_keys(Keys.BACKSPACE)     # Clear
            time.sleep(1)
            date_input.send_keys(journey_date)       # Type the date in dd/MM/yyyy
            date_input.send_keys(Keys.TAB)           # Confirm date selection
            print(f"✅ Journey Date set to {journey_date}")
                  
                  
                  #<span _ngcontent-qav-c112="" class="fare-icon fa fa-info-circle fa-lg hidden-xs ng-star-inserted"></span>                                                  
            
            
            
            # 4. Click Search
            search_button_xpath = "//button[contains(@class, 'train_Search') and text()='Search']"
            self.wait.until(EC.element_to_be_clickable((By.XPATH, search_button_xpath))).click()
            print("✅ Search complete. Waiting for train list...")

            # 5. Find train container by train number
            train_container_xpath = f"//div[contains(@class, 'bull-back') and .//strong[contains(text(), '{train_no}')]]"
            train_container = self.wait.until(EC.presence_of_element_located((By.XPATH, train_container_xpath)))
            print(f"✅ Found container for Train No. '{train_no}'.")

            # 6. Find the section that contains the class code (like '3A')
            class_section_xpath = f".//div[contains(@class, 'pre-avl') and contains(., '{class_code}')]"
            class_section = train_container.find_element(By.XPATH, class_section_xpath)
            print(f"✅ Found class section for '{class_code}'.")

            # 7. Find and click the refresh icon inside this class section
            refresh_icon_xpath = ".//span[contains(@class, 'fa-repeat')]"
            refresh_icon = class_section.find_element(By.XPATH, refresh_icon_xpath)
            self.wait.until(EC.element_to_be_clickable((By.XPATH, refresh_icon_xpath)))
            refresh_icon.click()
            print("✅ Refresh button clicked for the selected class.")

            time.sleep(10)  # Optional: wait to see the result

        except TimeoutException:
            print(f"❌ Operation timed out. Could not find an element in the sequence.")
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")

    def close(self):
        self.driver.quit()
        print("\n🤖 Browser session closed.")


# --- How to use the final bot ---
if __name__ == "__main__":
    bot = IRCTCTrainBot()

    bot.check_availability(
        from_station="ANVT",
        from_name="ANAND VIHAR TRM",
        to_station="LKO",
        to_name="LUCKNOW NR",
        train_no="82502",
        class_code="CC",
        journey_date="27/08/2025"   # dd/MM/yyyy format
    )

    bot.close()
