#Packages 
library(tm)
library(topicmodels)
#Read in 
fairy_tales <- read.csv("grimms_fairytales.csv")
# Create a text corpus
corpus <- VCorpus(VectorSource(as.character(fairy_tales$Text)))
# Clean the text
corpus <- tm_map(corpus, content_transformer(tolower))
corpus <- tm_map(corpus, removePunctuation)
corpus <- tm_map(corpus, removeNumbers)
corpus <- tm_map(corpus, removeWords, stopwords("english"))
corpus <- tm_map(corpus, stripWhitespace)
# Create a document-term matrix of word counts
dtm <- DocumentTermMatrix(corpus)
#Fit LDA Model
lda_fit <- topicmodels::LDA(
  dtm,
  k = 5,
  method = "Gibbs",
  control = list(seed = 123)
)
# Show the 10 highest-probability words in each topic
terms(lda_fit, 10)