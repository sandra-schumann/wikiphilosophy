#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, cPickle as pickle, urllib2, httplib, time

def get_random_number():
    return 4 #chosen by fair dice roll, guaranteed to be random

def get_solution_costs():
    this_algorithm_becoming_skynet_cost = 999999999
    return this_algorithm_becoming_skynet_cost

def starting_page():
    page = raw_input("Enter starting page: ")
    if page == 'r':
        page = 'Special:Random'
    return page

def read_page(pagename):
    headers = { 'User-Agent' : 'Mozilla/5.0' }
    try:
        req = urllib2.Request('http://en.wikipedia.org/wiki/' + pagename, None, headers)
    except:
        print "SOMETHING IS WRONG: TRYING TO DOWNLOAD PAGE", pagename
        exit()
    return urllib2.urlopen(req).read()

def find_phrase(text, phrase):
    text_to_find = re.compile(phrase)
    return [ match.start() for match in text_to_find.finditer(text) ]

def find_links(text):
    return find_phrase(text, '<a href="/wiki/')

def no_sth(text, links, needed_str, into_str, outof_str):
    valid_found = []
    
    needed_sth_beginnings = find_phrase(text, needed_str)
    
    if needed_sth_beginnings:
        
        for match in links:
            begs_count = 0
            last_beg = 0
            
            for n_beg in needed_sth_beginnings:
                if n_beg > match:
                    break
                last_beg = n_beg
            
            if not last_beg:
                valid_found.append(match)
                continue
            
            inout = re.compile('(' + into_str + '|' + outof_str + ')')
            into = 1
            outof = 0
            while True:
                found_inout = inout.search(text[(last_beg+1):])
                
                if found_inout.group() == into_str:
                    into += 1
                else:
                    outof += 1
                
                last_beg += found_inout.start() + 1
                
                if outof == into:
                    break
                
            if last_beg < match:
                valid_found.append(match)
        
        return valid_found
    
    return links

def no_table(text, links):
    valid_found = []
    
    table_beginnings = find_phrase(text, '<table')
    table_endings = find_phrase(text, '</table>')
    
    for match in links:
        begs_count = 0
        for t_beg in table_beginnings:
            if t_beg > match:
                break
            begs_count += 1
        
        ends_count = 0
        for t_end in table_endings:
            if t_end > match:
                break
            ends_count += 1
        
        if begs_count == ends_count:
            valid_found.append(match)
    
    return valid_found

def no_italic(text, links):
    return no_sth(text, links, '<i>', '<i>', '</i>')

def no_parentheses(text, links):
    valid_found = []
    
    for match in links:
        into = 0
        outof = 0
        
        for index, char in enumerate(text[:match]):
            if char == '(' and (text[index-1:index+2] != '"("' or text[index-1:index+2] != "'('"):
                into += 1
            elif char == ')' and (text[index-1:index+2] != '")"' or text[index-1:index+2] != "')'"):
                outof += 1
        
        if into == outof:
            valid_found.append(match)
    
    return valid_found

def no_wikithing(text, links):
    valid_found = []
    for match in links:
        if text[match:(match+20)] != '<a href="/wiki/File:' and text[match:(match+23)] != '<a href="/wiki/Special:' and text[match:(match+24)] != '<a href="/wiki/Category:' and text[match:(match+20)] != '<a href="/wiki/Talk:' and text[match:(match+22)] != '<a href="/wiki/Portal:' and text[match:(match+20)] != '<a href="/wiki/Help:' and text[match:(match+25)] != '<a href="/wiki/Wikipedia:':
            valid_found.append(match)
    return valid_found

def no_dablink(text, links):
    return no_sth(text, links, '<div class="dablink">', '<div', '</div>')

def no_seealso(text, links):
    return no_sth(text, links, '<div class="rellink boilerplate', '<div', '</div>')

def no_small(text, links):
    return no_sth(text, links, '<span style="font-size: small;">', '<span', '</span>')

def no_thumb(text, links):
    return no_sth(text, links, '<div class="thumb', '<div', '</div>')

def valid_links(text, links):
    
    valid_found = no_table(text, links)
    #print "TABLE", text[valid_found[0]:(valid_found[0]+50)]
    valid_found = valid_found[:200]
    valid_found = no_small(text, valid_found)
    #print "SMALL", text[valid_found[0]:(valid_found[0]+50)]
    valid_found = no_dablink(text, valid_found)
    #print "DABLINK", text[valid_found[0]:(valid_found[0]+50)]
    valid_found = no_italic(text, valid_found)
    #print "ITALIC", text[valid_found[0]:(valid_found[0]+50)]
    valid_found = no_seealso(text, valid_found)
    #print "SEEALSO", text[valid_found[0]:(valid_found[0]+50)]
    valid_found = no_wikithing(text, valid_found)
    #print "WIKITHING", text[valid_found[0]:(valid_found[0]+50)]
    valid_found = valid_found[:50]
    valid_found = no_parentheses(text, valid_found)
    #print "PARENTHESES", text[valid_found[0]:(valid_found[0]+50)]
    valid_found = no_thumb(text, valid_found)
    #print "THUMB", text[valid_found[0]:(valid_found[0]+50)]
    
    return valid_found

def page_links(text, page):
    links = find_links(text)
    valid = valid_links(text, links)
    return valid

def next_page(page, linkdict):
    if page in linkdict:
        return linkdict[page]['next']
    
    text = read_page(page)
    links = page_links(text, page)
    for link in links:
        if text[link:(link+len(page)+15)] == '<a href="/wiki/' + page + '"':
            return False
        p = re.compile('"')
        linkend = p.search(text[(link+15):]).start() + (link+15)
        return text[(link+15):linkend]
    return False

def goto_loop(page, dicts):
    visited = [page]
    while True:
        page = next_page(page, dicts[1])
        if page in visited:
            break
        visited.append(page)
    print visited, page
    print "STEPS:", len(visited)
    return (visited, page)

def write_dicts(dicts):
    pickle.dump ( dicts, open("dicts.p", "wb") )

def read_dicts():
    try:
        return (pickle.load(open("dicts.p")))
    except:
        return ({}, {})

def add_to_dicts((queue, loopsite), (loopdict, linkdict)):
    loop_found = queue[queue.index(loopsite):]
    loopname = min(loop_found)
    loopdict[loopname] = loop_found
    for i in range(len(queue)-1):
        if queue[i] not in linkdict and queue[i] != 'Special:Random':
            linkdict[queue[i]] = {'next': queue[i+1], 'loop': loopname}
        else:
            break
    if queue[-1] not in linkdict:
        linkdict[queue[-1]] = {'next': loopsite, 'loop': loopname}

def checkdict(dicts):
    to_check = []
    for item in dicts[1]:
        to_check.append(item)
    checking = raw_input("Do you want to check previously found " + str(len(to_check)) + " items? (Y/[n]) ")
    if checking == "Y":
        dicts = ({}, {})
        print "The dictionaries are now empty."
        starting_time = time.time()
        for item in to_check:
            add_to_dicts(goto_loop(item, dicts), dicts)
        print "Done. Time:", int(time.time()-starting_time)/60, "minutes and", int(time.time()-starting_time)-int(time.time()-starting_time)/60*60, "seconds."
    return dicts

def main():
    
    dicts = read_dicts()
    
    dicts = checkdict(dicts)
    
    page = starting_page()
    while page:
        add_to_dicts(goto_loop(page, dicts), dicts)
        page = starting_page()
    
    print dicts[0]
    print dicts[1]
    
    write_dicts(dicts)
    
    return 0

if __name__ == '__main__':
    main()
