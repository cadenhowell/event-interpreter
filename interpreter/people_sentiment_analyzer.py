import utilities
import re

def analyze_people(host_list, data):
    if host_list == []: return None
    host_hit_count = dict()
    host_analysis = dict()
    for host in host_list:
        host_analysis[host] = 1
        host_hit_count[host] = 1
    for post in data:
        t = post['text']
        t_lower = t.lower()
        tnp = re.sub(r'[^\w\s]', '', post['text'])
        for host in host_list:
            if host in t_lower:
                sentiment = utilities.tweet_opinion(t)
                sentiment_score = sentiment[0]
                found_person = None
                if sentiment[1] != None: found_person = sentiment[1].lower()
                if found_person == host:
                    host_hit_count[host] += 3
                    host_analysis[host] += 3*sentiment_score
                else:
                    host_hit_count[host] += 1
                    host_analysis[host] += sentiment_score

    for host, value in host_analysis.items():
        host_analysis[host] = value / host_hit_count[host]

    return host_analysis