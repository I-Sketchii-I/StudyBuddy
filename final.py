from PyQt5 import QtCore, QtGui, QtWidgets
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import requests
import re
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

# Please don't steal my API Keys
my_api_key = ''
my_cse_id = ''

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.SearchBar = QtWidgets.QLineEdit(self.centralwidget)
        self.SearchBar.setGeometry(QtCore.QRect(20, 20, 201, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.SearchBar.setFont(font)
        self.SearchBar.setObjectName("SearchBar")

        self.SearchButton = QtWidgets.QPushButton(self.centralwidget)
        self.SearchButton.setGeometry(QtCore.QRect(230, 20, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.SearchButton.setFont(font)
        self.SearchButton.setObjectName("SearchButton")

        self.RelatedScrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.RelatedScrollArea.setGeometry(QtCore.QRect(20, 110, 201, 281))
        self.RelatedScrollArea.setWidgetResizable(True)
        self.RelatedScrollArea.setObjectName("RelatedScrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 199, 279))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        self.RelatedText = QtWidgets.QTextEdit(self.scrollAreaWidgetContents)
        self.RelatedText.setGeometry(QtCore.QRect(0, 0, 201, 281))
        self.RelatedText.setObjectName("RelatedText")
        self.RelatedScrollArea.setWidget(self.scrollAreaWidgetContents)

        self.RelatedLabel = QtWidgets.QLabel(self.centralwidget)
        self.RelatedLabel.setGeometry(QtCore.QRect(20, 82, 101, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.RelatedLabel.setFont(font)
        self.RelatedLabel.setObjectName("RelatedLabel")

        self.SummaryScrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.SummaryScrollArea.setGeometry(QtCore.QRect(349, 110, 411, 281))
        self.SummaryScrollArea.setWidgetResizable(True)
        self.SummaryScrollArea.setObjectName("SummaryScrollArea")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 409, 279))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")

        self.SummaryText = QtWidgets.QTextBrowser(self.scrollAreaWidgetContents_2)
        self.SummaryText.setGeometry(QtCore.QRect(0, 0, 411, 281))
        self.SummaryText.setObjectName("SummaryText")
        self.SummaryScrollArea.setWidget(self.scrollAreaWidgetContents_2)

        self.SummaryLabel = QtWidgets.QLabel(self.centralwidget)
        self.SummaryLabel.setGeometry(QtCore.QRect(350, 80, 101, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.SummaryLabel.setFont(font)
        self.SummaryLabel.setObjectName("SummaryLabel")

        self.SentenceLabel = QtWidgets.QLabel(self.centralwidget)
        self.SentenceLabel.setGeometry(QtCore.QRect(610, 80, 101, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.SentenceLabel.setFont(font)
        self.SentenceLabel.setObjectName("SentenceLabel")

        self.NumBox = QtWidgets.QSpinBox(self.centralwidget)
        self.NumBox.setGeometry(QtCore.QRect(710, 80, 42, 22))
        self.NumBox.setObjectName("NumBox")

        self.HelpButton = QtWidgets.QPushButton(self.centralwidget)
        self.HelpButton.setGeometry(QtCore.QRect(664, 522, 111, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.HelpButton.setFont(font)
        self.HelpButton.setText("Need Help?")
        self.HelpButton.setObjectName("HelpButton")

        self.HelpMsg = QtWidgets.QMessageBox()
        self.HelpMsg.setWindowTitle("Welcome to StudyBuddy!")
        self.HelpMsg.setText("StudyBuddy is tool that scrapes and summarizes searches from Google.\nSimply type in what you want to search, enter how many sentences you want the summary to be, and hit search!")

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Method to execute the search from the GUI
        self.SearchButton.clicked.connect(lambda: self.search(self.SearchBar.text(), self.NumBox.value()))
        # method to show the help popup window
        self.HelpButton.clicked.connect(lambda: self.HelpMsg.exec_())

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Resurge Assistant"))
        self.SearchButton.setText(_translate("MainWindow", "Search"))
        self.RelatedLabel.setText(_translate("MainWindow", "Related"))
        self.SummaryLabel.setText(_translate("MainWindow", "Summary"))
        self.SentenceLabel.setText(_translate("MainWindow", "# of Sentences:"))

    # Main Search Method
    def search(self, text, num):
        # Clear both Summary and Related text boxes
        self.SummaryText.clear()
        self.RelatedText.clear()
        # Use search method to get google results
        results = google_search(text, my_api_key, my_cse_id)
        # store the top 3 result's urls
        urls = [results[0]['formattedUrl'], results[1]['formattedUrl'], results[2]['formattedUrl']]
        # scrape each url for their text
        x1 = scrape(urls[0])
        x2 = scrape(urls[1])
        x3 = scrape(urls[2])
        # combine all 3 result strings into 1
        y = x1 + x2 + x3
        # get the summary and set the text to the text box
        self.SummaryText.setText(sum(y, num))
        # Store top 10 result titles in a list
        related = [results[0]['title'], results[1]['title'], results[2]['title'], results[3]['title'], results[4]['title'], results[5]['title'], results[6]['title'], results[7]['title'], results[8]['title']]
        # convert list to a string
        related = '\n'.join([str(item) for item in related])
        # Set the realte text box and clear the search bar
        self.RelatedText.setText(related)
        self.SearchBar.clear()

# Method to use custom google search engine results
def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    # returns search result data
    return res['items']

# Method to scrape the sites paragraphs and strip them to base text
def scrape(url):
    # Convert url contents to soup
    site = requests.get(url)
    src = site.content
    soup = BeautifulSoup(src, 'lxml')
    # find all paragraph tags
    x = soup.find_all('p')
    # remove unecessary tag
    x.pop(0)
    # convert the data to a string and clean it up using regex
    y = ''.join(str(e) for e in x)
    clean = re.compile('<.*?>')
    y = re.sub(clean, '', y)
    y = re.sub(r'\[[0-9]*\]', ' ', y)
    # return the string of scraped text
    return y

# Summarization Method
def sum(text, num):
    # grab sumy parser and set language
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    # create the summarizer
    summarizer = LsaSummarizer(Stemmer("english"))
    # get the stop words for our summarizer
    summarizer.stop_words = get_stop_words("english")
    # put summarized sentences to a string and return it
    x = ""
    for sentence in summarizer(parser.document, num):
        x += str(sentence)
    return x

# Main Method
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
