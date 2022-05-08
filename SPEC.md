# Methodology Ideas

## Data Processing - Concurrent Approach

Step 1: 
- Parse by tweet and identify names and keywords - i.e name "John Doe" and keyword "host,presented,nominated,won"
- Analyze tweet and determine subject, sentiment, or any other relevant information through NLP. Say a nominee and a presenter are in the same tweet, usually the nominee is the more important subject in the tweet. 
- Determine validity importance of tweet, rank tweet on scale. 
- Without determining significance of names/keywords, store trimmed tweets with associated metadata in mongodb.

Step 2: 
- Parse trimmed tweets, and depending on keyword/metadata determine (with some confidence scale) what role the person in the tweet has. Either host, presenter, nominee, winner. As more tweets are processed, more confidence that a certain person is a certain role can be determined. Take advantage of the overlap between some categories, e.g. "wins" should count towards nominees.
- At the end of processing simply use the candidates for each role with the highest confidence number.

