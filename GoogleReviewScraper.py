#import libraries
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os

# get terminal size
terminal_size = os.get_terminal_size()

# menu


def menu():
    print('Google Review Scraper \n')
    print('[1] --- Enter a URL')
    print('[0] --- Exit')
    print('=' * terminal_size.columns)

#url = 'https://www.google.com/search?rlz=1C5CHFA_enSG968SG971&sxsrf=ALiCzsZaN3KFnybtff-FeJ4uxxmVRUja3Q:1671020894391&q=subway+le+quest&spell=1&sa=X&ved=2ahUKEwiS1cn2jfn7AhWaTmwGHcQJDcoQBSgAegQIBRAB&biw=1440&bih=796&dpr=2'
#url = 'https://www.google.com/search?q=le+quest+bar&rlz=1C5CHFA_enSG968SG971&sxsrf=ALiCzsaZl4qXi16WHw3YM0HKBazf9nIIKQ%3A1671023257575&ei=mcqZY_TPIuqXseMP2LKEuAc&ved=0ahUKEwi0gLfdlvn7AhXqS2wGHVgZAXcQ4dUDCA8&uact=5&oq=le+quest+bar&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQAzIECCMQJzIQCC4QgAQQhwIQxwEQrwEQFDIFCAAQgAQyCAgAEBYQHhAPMgUIABCGAzIFCAAQhgM6CggAEEcQ1gQQsAM6DQgAEEcQ1gQQyQMQsAM6CAgAEJIDELADOgYIABAWEB46CAgAEBYQHhAKOgsILhDHARCvARCRAjoLCC4QgAQQxwEQrwE6CwguEK8BEMcBEIAEOgsILhCvARDHARCRAjoFCAAQkQI6EAguEK8BEMcBEIcCEIAEEBRKBAhBGABKBAhGGABQjwNYxQ9gwhBoAXABeACAAY4BiAHDBZIBAzkuMZgBAKABAcgBCcABAQ&sclient=gws-wiz-serp'


def main():

    # counter to save review to csv file
    i = 1
    menu()
    option = int(input('Please enter an option:  '))

    while option != 0:
        if option == 1:

            # get url
            url = input("Please enter a url:  ")

            # driver code
            chrome_driver_path = r"\driver\chromedriver.exe"
            options = webdriver.ChromeOptions()
            driver = webdriver.Chrome(
                executable_path=chrome_driver_path, options=options)
            driver.get(url)
            print('\n')

            # get name, address and average rating of the business
            try:
                name = driver.find_element(
                    'xpath', '//div[@class="SPZz6b"]').text.split()[0]
                print(f"Business: {name}\n")

                address = driver.find_element(
                    'xpath', '//span[@class="LrzXr"]').text
                print(f"Address: {address}\n")

                rating_average = driver.find_element(
                    'xpath', '//span[@class="Aq14fc"]').text
                print(f"Average Rating: {rating_average}\n")
            except NoSuchElementException:
                print("Please check the url and try again..  \n")

            # get total number of reviews
            total_reviews_str = driver.find_element(
                'xpath', '//span[@class="hqzQac"]').text
            total_reviews = int(total_reviews_str.split()[0])

            # click on reviews
            driver.find_element('xpath', '//span[@class="hqzQac"]').click()
            time.sleep(3)

            pop_up_window = WebDriverWait(
                driver, 2).until(EC.element_to_be_clickable(
                    (By.XPATH, "//div[@class='review-dialog-list']")))
            time.sleep(3)

            # to get the app to scroll to the bottom of the reviews
            while True:
                count = 0
                driver.execute_script(
                    'arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;',
                    pop_up_window)
                counter = driver.find_elements(
                    'xpath', "//div[@jscontroller='fIQYlf']")
                for each in counter:
                    count += 1
                    # if check_exists_by_xpath("//a[@class='review-more-link']") == True:
                    #     driver.find_element(
                    #         'xpath', './/a[@class="review-more-link"]').click()
                if count == total_reviews:
                    break
                time.sleep(1)

            # to find reviews that are hidden when its too long and click on them
            try:
                more = driver.find_elements(
                    'xpath', '//a[@class="review-more-link"]')
                for e in more:
                    e.click()
            except NoSuchElementException:
                print()

            time.sleep(1)

            # get the individual reviews
            reviews = driver.find_elements(
                'xpath', "//div[@jscontroller='fIQYlf']")

            review_list = []

            name_rating = {
                'Business': name,
                'Address': address,
                'Average rating': rating_average
            }
            review_list.append(name_rating)

            # getting the data and appending it into the review list to export into a dataframe and eventually a csv
            for review in reviews:
                rating = review.find_element(
                    'xpath', ".//span[@class='Fam1ne EBe2gf']")
                rating_text = rating.get_attribute("aria-label")
                # changing the rating text to int so it can be filtered
                if rating_text == 'Rated 5.0 out of 5,':
                    rating_text = 5
                if rating_text == 'Rated 4.0 out of 5,':
                    rating_text = 4
                if rating_text == 'Rated 3.0 out of 5,':
                    rating_text = 3
                if rating_text == 'Rated 2.0 out of 5,':
                    rating_text = 2
                if rating_text == 'Rated 1.0 out of 5,':
                    rating_text = 1

                time_period = review.find_element(
                    'xpath', './/span[@class="dehysf lTi8oc"]').text
                review_text = review.find_element(
                    'xpath', './/span[@jscontroller="MZnM8e"]').text
                if review_text == '':
                    review_text = 'No Text'
                review_item = {
                    'Review': review_text,
                    'Rated out of 5.0': rating_text,
                    'Rated time': time_period
                }

                review_list.append(review_item)

            df = pd.DataFrame(review_list)
            df.to_csv('Review' + str(i) + '.csv', sep='\t', encoding='utf-16')
            print('Reviews successfully saved into CSV file.. \n')
            i += 1
            driver.close()
            pass
        else:
            print("Invalid Option! Please enter another input:  ")

        menu()
        option = int(input('Please enter an option:  '))
    driver.close()
    print("Program exited successfully..")


main()
