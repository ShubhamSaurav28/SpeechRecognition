from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import psutil
import sys

# XPath for the "Clear" button in the dictation.io interface
clear_button_xpath = '//*[@id="dictation"]/div[2]/div/div[3]/div[2]/a[8]'

# Function to print a countdown in the console
def print_countdown(seconds):
    for i in range(seconds, 0, -1):
        sys.stdout.write(f"Starting in {i} seconds...")
        sys.stdout.flush()
        time.sleep(1)
        sys.stdout.write('\r\033[K')  # Clear the line
        sys.stdout.flush()
    print("Recognizing...")  # Print "Recognizing..." after the countdown

# Function to perform dictation transcription using Selenium
def transcribe_from_dictation_io():
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    chrome_options.add_argument("--enable-media-stream")
    
    # Path to the ChromeDriver executable
    chromedriver_path = 'chromedriver.exe'
    
    # Create a ChromeDriver instance with the specified options
    service = ChromeService(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Open the dictation.io website
        driver.get('https://dictation.io/speech')
        
        # Minimize the browser window
        driver.minimize_window()
        
        # Print a countdown before starting dictation
        print_countdown(15)
        
        # Perform initial setup (handling cookies and starting dictation)
        cookie_area = driver.find_element(By.XPATH, '/html/body/div[1]/div/a')
        cookie_area.click()
        dictation_area = driver.find_element(By.XPATH, '//*[@id="dictation"]/div[2]/div/div[3]/div[1]/a')
        dictation_area.click()
        time.sleep(5)

        # Continuous loop for dictation
        while True:
            # Get the text from the dictation area
            notetext = driver.find_element(By.XPATH, '//*[@id="speech"]').text.strip()

            # If there is new text, clear the dictation area and write to a file
            if notetext:
                driver.find_element(By.XPATH, clear_button_xpath).click()
                output_file_path = "transcription.txt"
                with open(output_file_path, "w") as file_write:
                    file_write.write(notetext)

            time.sleep(2)

    except KeyboardInterrupt:
        # Handle Ctrl+C interrupt
        print("\nCtrl+C pressed: Stopping dictation...")
    except Exception as e:
        # Handle other exceptions
        print(f"An error occurred: {str(e)}")
    finally:
        try:
            # Close the browser and associated processes
            if driver is not None:
                browser_process = psutil.Process(driver.service.process.pid)
                for child_process in browser_process.children(recursive=True):
                    child_process.terminate()
                browser_process.terminate()
                driver.quit()
        except Exception as e:
            # Handle errors during cleanup
            print(f"An error occurred while closing the browser: {str(e)}")

# Entry point of the script
if __name__ == "__main__":
    try:
        # Call the main function for dictation transcription
        transcribe_from_dictation_io()
    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred: {str(e)}")

