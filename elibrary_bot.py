import telebot
from telebot import types
import sqlite3
import re

bot = telebot.TeleBot("1835888768:AAHb-RBp8MjdH_-NLSUeCGtoOlRN7lxefW0", parse_mode=None)

mainInlineMarkup = types.InlineKeyboardMarkup(row_width=3)
searchInlineButton = types.InlineKeyboardButton("Search", callback_data="search")
resetFiltersInlineButton = types.InlineKeyboardButton("Reset", callback_data="reset")
mainInlineMarkup.row(searchInlineButton)
mainInlineMarkup.row(resetFiltersInlineButton)
mainMarkupCallbackData = [searchInlineButton.callback_data, resetFiltersInlineButton.callback_data]

start_message = "Enter search filters and press search: \nFor further information type /help"

help_message = "Valid Filters are: ISBN, Genre, Title, Date(publish date), Count, Language, bPrice(bottom price), tPrice(top price)\n" \
    "fName(author's first name), sName(author's second name)\nCompany(publisher's company name)\n" \
    "You need to write whatever filters you wish to use like so \"FILTER_NAME FILTER_VALUE\" and then press Search(e.g. Genre Comedy)" \
    "If you wish to drop filter simply type \"Drop FILTER_NAME\" or press the Reset button to drop all filters at once"

isbn = ""
genre = ""
title = ""
publishDate = ""
pageCount = ""
language = ""
bottomPrice = ""
topPrice = ""
firstName = ""
secondName = ""
companyName = ""
filters = [isbn, genre, title, publishDate, pageCount, language, bottomPrice, topPrice, firstName, secondName, companyName]


@bot.message_handler(commands=['start'])
def start_action(message):
    bot.send_message(message.chat.id, start_message, reply_markup=mainInlineMarkup)

@bot.message_handler(commands=['help'])
def help_action(message):
    bot.send_message(message.chat.id, help_message)

@bot.message_handler(commands=['show'])
def show_action(message):
    outputMessage = ""
    filterNames = ["ISBN","Genre","Title","Publication Date","Count","Language","Price","First Name","Second Name","Company"]
    for filter_index, filter in enumerate(filters):
        if len(filter) > 0:
            outputMessage += filterNames[filter_index] + ": " + filter + '\n'
    if len(outputMessage) == 0:
        outputMessage = "No filters set yet!"
    bot.send_message(message.chat.id, outputMessage)

@bot.message_handler(regexp="ISBN \d{9}-\d{1}")
def set_isbn(message):
    global isbn
    isbn = message.text[5:]
    filters[0] = isbn
    bot.reply_to(message, "ISBN set!")

@bot.message_handler(regexp="(G|g)enre [a-zA-Z]+")
def set_genre(message):
    global genre
    genre = message.text[6:]
    filters[1] = genre
    bot.reply_to(message, "Genre set!")

@bot.message_handler(regexp="(T|t)itle [a-zA-Z]+")
def set_title(message):
    global title
    title = message.text[6:]
    filters[2] = title
    bot.reply_to(message, "Title set!")

@bot.message_handler(regexp="(D|d)ate \d{4}-\d{2}-\d{2}")
def set_publication_date(message):
    global publishDate
    publishDate = message.text[5:]
    filters[3] = publishDate
    bot.reply_to(message, "Publication date set!")

@bot.message_handler(regexp="(C|c)ount \d+")
def set_page_count(message):
    global pageCount
    pageCount = message.text[6:]
    filters[4] = pageCount
    bot.reply_to(message, "Page count set!")

@bot.message_handler(regexp="(L|l)anguage [a-zA-Z]+")
def set_language(message):
    global language
    language = message.text[9:]
    filters[5] = language
    bot.reply_to(message, "Language set!")

@bot.message_handler(regexp="bPrice \d+")
def set_bottom_price(message):
    global bottomPrice
    bottomPrice = message.text[7:]
    filters[6] = bottomPrice
    bot.reply_to(message, "Bottom price set!")

@bot.message_handler(regexp="tPrice \d+")
def set_top_price(message):
    global topPrice
    topPrice = message.text[7:]
    filters[7] = topPrice
    bot.reply_to(message, "Top price set!")

@bot.message_handler(regexp="fName [a-zA-Z]+")
def set_first_name(message):
    global firstName
    firstName = message.text[6:]
    filters[8] = firstName
    bot.reply_to(message, "First name set!")

@bot.message_handler(regexp="sName [a-zA-Z]+")
def set_second_name(message):
    global secondName
    secondName = message.text[6:]
    filters[9] = secondName
    bot.reply_to(message, "Second name set!")

@bot.message_handler(regexp="(C|c)ompany [a-zA-Z]+")
def set_company_name(message):
    global companyName
    companyName = message.text[8:]
    filters[10] = companyName
    bot.reply_to(message, "Company name set!")

@bot.message_handler(regexp="(D|d)rop [a-zA-Z]+")
def drop_filter(message):
    filterNames = [re.compile("ISBN", re.IGNORECASE), re.compile("Genre", re.IGNORECASE),
                   re.compile("Title", re.IGNORECASE), re.compile("Date", re.IGNORECASE),
                   re.compile("Count", re.IGNORECASE), re.compile("Language", re.IGNORECASE),
                   re.compile("Price", re.IGNORECASE), re.compile("fName", re.IGNORECASE),
                   re.compile("sName", re.IGNORECASE), re.compile("Company", re.IGNORECASE)]
    for index, filterName in enumerate(filterNames):
        if filterName.match(message.text[5:]):
            filters[index] = ""
            bot.reply_to(message, "Dropped!")


@bot.callback_query_handler(func=lambda call: call.data == mainMarkupCallbackData[0])
def search_callback_handler(call):
    bookFilterNames = ["isbn", "genre", "title", "publish_date", "page_count", "language", "price"]
    authorFilterNames = ["first_name", "last_name"]
    publisherFilterName = "name"
    query = "select * from Books \
                    inner join Books_Authors on Books.isbn = Books_Authors.ba_isbn \
                    inner join Authors on Books_Authors.author_id = Authors.id \
                    inner join Publishers on Books.publisher_id = Publishers.id \
                    where "
    queryTuple = ()
    connection = sqlite3.connect('eLibrary.db')
    cursor = connection.cursor()
    outputMessage = ""
    for filter_index, filter in enumerate(filters[:6]):
        if len(filter) > 0:
            query += bookFilterNames[filter_index] + "=? and "
            queryTuple += (filter,)
    for filter_index, filter in enumerate(filters[6:8]):
        if len(filter) > 0:
            if filter_index:
                query += bookFilterNames[filter_index + 6] + ">=? and "
            else:
                query += bookFilterNames[filter_index + 6] + "<=? and "
            queryTuple += (filter,)
    for filter_index, filter in enumerate(filters[8:10]):
        if len(filter) > 0:
            query += authorFilterNames[filter_index] + "=? and "
            queryTuple += (filter,)
    if len(filters[10]) > 0:
        query += publisherFilterName + "=? and "
        queryTuple += (filter,)
    query = query[:-5]
    rs = cursor.execute(query, queryTuple)
    for r in rs:
        r = r[0:1] + r[2:8] + r[11:13] + r[14:]
        author = ' '.join(r[7:9])
        r = r[0:7] + (author,) + r[9:]
        outputMessage += ', '.join(map(str, r)) + '\n'

    bot.send_message(call.message.chat.id, outputMessage)

@bot.callback_query_handler(func=lambda call: call.data == mainMarkupCallbackData[1])
def search_callback_handler(call):
    for filter_index in range(len(filters)):
        filters[filter_index] = ""
    bot.send_message(call.message.chat.id, "All filters dropped!")

bot.polling()