import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from collections import Counter 
import en_coref_md
import spacy
import re
from spacy.matcher import Matcher 
from spacy import displacy 
from IPython.display import Image, display
from newspaper import Article

nlp=spacy.load('en_core_web_md')
nlp_2 = en_coref_md.load()



# function to preprocess speech
def clean(text):
    # removing paragraph numbers
    text = re.sub('[0-9]+.\t','',str(text))
    # removing new line characters
    text = re.sub('\n ','',str(text))
    text = re.sub('\n',' ',str(text))
    # removing apostrophes
    text = re.sub("'s",'',str(text))
    # removing hyphens
    text = re.sub("-",' ',str(text))
    text = re.sub("— ",'',str(text))
    # removing quotation marks
    text = re.sub('\"','',str(text))
    text = re.sub('  \t','',str(text))
    text = re.sub(' \t','', str(text))
    text = re.sub('\t','',str(text))
    # removing salutations
    text = re.sub("Mr\.",'Mr',str(text))
    text = re.sub("Mrs\.",'Mrs',str(text))
    # removing any reference to outside text
    text = re.sub("[\(\[].*?[\)\]]", "", str(text))
    return text
# preprocessing speeches
#df['Speech_clean'] = df['Speech'].apply(clean)


def sentences(text):
    # split sentences and questions
    text = re.split('[.?]', text)
    clean_sent = []
    for sent in text:
        clean_sent.append(sent)
    return clean_sent
# sentences




def replace_names(text):
    dummy = text
    name_list = []
    doc = nlp_2(text)
    for ent in doc.ents:
        if(ent.label_ == 'PERSON'):
            name_list.append(ent.text)
    if(doc._.has_coref):
        for cluster in doc._.coref_clusters:
            if(cluster.main.text in name_list):
                for m in cluster.mentions:
                    if(m != cluster.main):
                        pos1 = dummy[:m.start_char]
                        pos2 = dummy[m.start_char-1:]                        
                        pos2 = pos2.replace(str(m),str(cluster.main),1)
                        dummy = pos1+pos2
    return dummy    
    
    
    
# rule to extract initiative name
def sent_subtree(text):
    # pattern match for schemes or initiatives
    patterns = [r'\b(?i)'+'invent'+r'\b(?i)',
                r'\b(?i)'+'invented'+r'\b(?i)',
                r'\b(?i)'+'invention'+r'\b(?i)',
                r'\b(?i)'+'inventions'+r'\b(?i)',
                r'\b(?i)'+'plan'+r'\b(?i)',
           r'\b(?i)'+'programme'+r'\b(?i)',
           r'\b(?i)'+'scheme'+r'\b(?i)',
           r'\b(?i)'+'campaign'+r'\b(?i)',
           r'\b(?i)'+'initiative'+r'\b(?i)',
           r'\b(?i)'+'conference'+r'\b(?i)',
           r'\b(?i)'+'agreement'+r'\b(?i)',
           r'\b(?i)'+'alliance'+r'\b(?i)',
           r'\b(?i)'+'profit'+r'\b(?i)',
           r'\b(?i)'+'announce'+r'\b(?i)',
           r'\b(?i)'+'announces'+r'\b(?i)',
           r'\b(?i)'+'announcement'+r'\b(?i)',
           r'\b(?i)'+'vision'+r'\b(?i)', 
            r'\b(?i)'+'founder'+r'\b(?i)', 
               r'\b(?i)'+'ceo'+r'\b(?i)',
               r'\b(?i)'+'loss'+r'\b(?i)',
               r'\b(?i)'+'goal'+r'\b(?i)',
               r'\b(?i)'+'co-founder'+r'\b(?i)',
               r'\b(?i)'+'boss'+r'\b(?i)',
               r'\b(?i)'+'launch'+r'\b(?i)',
               r'\b(?i)'+'launches'+r'\b(?i)',
               r'\b(?i)'+'fund'+r'\b(?i)',
                r'\b(?i)'+'funding'+r'\b(?i)',
                r'\b(?i)'+'funds'+r'\b(?i)',
               r'\b(?i)'+'fundings'+r'\b(?i)',
               r'\b(?i)'+'step'+r'\b(?i)', 
                r'\b(?i)'+'launched'+r'\b(?i)',
                r'\b(?i)'+'approval'+r'\b(?i)',
                r'\b(?i)'+'approved'+r'\b(?i)',
                r'\b(?i)'+'approvals'+r'\b(?i)',
                r'\b(?i)'+'approves'+r'\b(?i)',
                r'\b(?i)'+'innovation'+r'\b(?i)',
                r'\b(?i)'+'innovations'+r'\b(?i)',
                r'\b(?i)'+'roll out'+r'\b(?i)',
                r'\b(?i)'+'features'+r'\b(?i)',
                r'\b(?i)'+'feature'+r'\b(?i)',
                r'\b(?i)'+'users'+r'\b(?i)',
                r'\b(?i)'+'user'+r'\b(?i)',
                r'\b(?i)'+'acquire'+r'\b(?i)',
                r'\b(?i)'+'acquires'+r'\b(?i)',
                r'\b(?i)'+'acquired'+r'\b(?i)',
                r'\b(?i)'+'fired'+r'\b(?i)',
                r'\b(?i)'+'fire'+r'\b(?i)',
                r'\b(?i)'+'hire'+r'\b(?i)',
                r'\b(?i)'+'hired'+r'\b(?i)',
                r'\b(?i)'+'share'+r'\b(?i)',
                r'\b(?i)'+'enable'+r'\b(?i)', 
                r'\b(?i)'+'enabling'+r'\b(?i)',
                r'\b(?i)'+'incident'+r'\b(?i)', 
                r'\b(?i)'+'incidents'+r'\b(?i)',
                r'\b(?i)'+'employee'+r'\b(?i)',
                r'\b(?i)'+'employees'+r'\b(?i)',
                r'\b(?i)'+'own'+r'\b(?i)',
                r'\b(?i)'+'owners'+r'\b(?i)',
                r'\b(?i)'+'revenue'+r'\b(?i)',
                r'\b(?i)'+'revenues'+r'\b(?i)',
                r'\b(?i)'+'reports'+r'\b(?i)',
                r'\b(?i)'+'report'+r'\b(?i)'
               ]
    schemes = []
    text = replace_names(text)
    doc = nlp(text)
    flag = 0
    # if no initiative present in sentence
    for pat in patterns:
        #print(pat)
        if re.search(pat, text) != None:
            flag = 1
            break
    if flag == 0:
        return schemes
    # iterating over sentence tokens
    for token in doc:
        for pat in patterns:
            #print(pat)
            # if we get a pattern match
            if re.search(pat, token.text) != None:

                
                # iterating over token subtree
                for node in token.subtree:
                   
                    word = ''
                    # only extract the proper nouns
                    if (node.pos_ == 'PROPN'):

                        if (doc[node.i+1].pos_=='PROPN'):
                            if (doc[node.i+2].pos_=='PROPN'):
                                word += node.text+' '+doc[node.i+1].text+' '+doc[node.i+2].text

                                
                            else:
                                word += node.text+' '+doc[node.i+1].text
                                
                        else:
                            word += node.text
                            
                            

        #removing singl name with full name
                    if len(word)!=0:
                        schemes.append(word)
#     print(schemes)
    #print(schemes, 'gaurav')
    single_name, full_name=[], []
    for i in schemes:
        if ' ' not in i:
            single_name.append(i)
        else:
            full_name.append(i)

    k = []
    for i in single_name:
        for j in full_name:
            if len(single_name)==len(full_name):
                if i in j:
                    k.append(j)
            else:
                if i in j:
                    k.append(j)
                if i not in j:
                    k.append(i)
        if len(full_name)==0:
            k.append(i)
    
    return list(set(k)) 
# derive initiatives



def sent_subtree_1(text):
    # pattern match for schemes or initiatives
    patterns = ['sector',
                'sectors',
                'industry',
                'industries',
                'digital payment',
                'digital payments',
                'digitals payment',
                "digital's payment",
                'market',
                'markets',
                'companies',
                'transformation',
                'transformations'
               ]
    schemes = []
    text = replace_names(text)
    doc = nlp(text)
    flag = 0
    # if no initiative present in sentence
    for pat in patterns:
        #print(pat)
        if re.search(pat, text) != None:
            flag = 1
            break
    if flag == 0:
        return schemes
    # iterating over sentence tokens
    for token in doc:
        for pat in patterns:
            # if we get a pattern match
            if re.search(pat, token.text) != None:
                # iterating over token subtree
                for node in token.subtree:
                    word = ''
                    # only extract the proper nouns
                    if (node.pos_ == 'PROPN'):
                        if (doc[node.i+1].pos_=='PROPN'):
                            if (doc[node.i+2].pos_=='PROPN'):
                                word += node.text+' '+doc[node.i+1].text+' '+doc[node.i+2].text
                            else:
                                word += node.text+' '+doc[node.i+1].text
                        else:
                            word += node.text
#                     print(word)
        #removing singl name with full name
                    if len(word)!=0:
                        schemes.append(word)
    #print(schemes, 'gaurav')
    single_name, full_name=[], []
    for i in schemes:
        if ' ' not in i:
            single_name.append(i)
        else:
            full_name.append(i)

    k = []
    for i in single_name:
        for j in full_name:
            if len(single_name)==len(full_name):
                if i in j:
                    k.append(j)
            else:
                if i in j:
                    k.append(j)
                if i not in j:
                    k.append(i)
        if len(full_name)==0:
            k.append(i)
    
    return list(set(k))    
# derive initiatives

#double_quotes string characters
def double_quotes(headline, text):
    L=[]
    import re
    doc = nlp(headline)
    l = [ent.text for ent in doc.ents if ent.label_=='ORG' or ent.label_=='PERSON']
    matches=re.findall(r'\"(.+?)\"',text)
    x =  ",".join(matches).split(',')
    for i in x:
        if i in l:
            L.append(i)
    return L
    
    
def headlines_person_unique(headline, text):
    d = {}
    
    doc = nlp(headline)
    doc1  = nlp(text)
    l = [ent.text for ent in doc.ents if ent.label_=='PERSON']
    m  = [ent.text for ent in doc1.ents if ent.label_=='PERSON']
    for x in set(l):
        d[x] = text.count(x)
    c = 0
    for k,v in d.items():
        if v==1:
            c=c+1
    return c / len(m) if len(m) != 0 else 0

def headlines_org_unique(headline, text):
    d = {}
    
    doc = nlp(headline)
    doc1  = nlp(text)
    l = [ent.text for ent in doc1.ents if ent.label_=='ORG']
    m = [ent.text for ent in doc.ents if ent.label_=='ORG']
    for x in set(m):
        d[x] = text.count(x)
    c = 0
    for k,v in d.items():
        if v==1:
            c=c+1
    return c / len(l) if len(l) != 0 else 0


def headlines_person_multiple(headline, text):
    d = {}
    
    doc = nlp(headline)
    doc1  = nlp(text)
    l = [ent.text for ent in doc.ents if ent.label_=='PERSON']
    m  = [ent.text for ent in doc1.ents if ent.label_=='PERSON']
    for x in set(l):
        d[x] = text.count(x)
    c = 0
    for k,v in d.items():
        if v!=1:
            c=c+1
    return c / len(m) if len(m) != 0 else 0

def headlines_org_multiple(headline, text):
    d = {}
    
    doc = nlp(headline)
    doc1  = nlp(text)
    l = [ent.text for ent in doc1.ents if ent.label_=='ORG']
    m = [ent.text for ent in doc.ents if ent.label_=='ORG']
    for x in set(m):
        d[x] = text.count(x)
    c = 0
    for k,v in d.items():
        if v!=1:
            c=c+1
    return c / len(l) if len(l) != 0 else 0


import spacy
#nlp = spacy.load('en_core_web_md', disable = ['ner','textcat'])
def rule1(headline, text):
    
    length = len(sentences(text))
    doc = nlp(text)
    
    sent = []
    
    for token in doc:
        
        # if the token is a verb
        if (token.pos_=='VERB'):
            
            phrase =''
            
            # only extract noun or pronoun subjects
            for sub_tok in token.lefts:
                
                if (sub_tok.dep_ in ['nsubj','nsubjpass']) and (sub_tok.pos_ in ['NOUN','PROPN','PRON']):
                    if sub_tok.text in headline:

                        # add subject to the phrase
                        phrase += sub_tok.text

                        # save the root of the verb in phrase
                        phrase += ' '+token.lemma_ 

                        # check for noun or pronoun direct objects
                        for sub_tok in token.rights:

                            # save the object in the phrase
                            if (sub_tok.dep_ in ['dobj']) and (sub_tok.pos_ in ['NOUN','PROPN']):

                                phrase += ' '+sub_tok.text
                                sent.append(phrase)
#     print(sent, 'test')

    return len(sent)/length
    
    
# function for rule 2 adjective using headline and body
def rule2(headline, text):
    length = len(sentences(text))
  
    doc = nlp(text)

    pat = []
    
    # iterate over tokens
    for token in doc:
        phrase = ''
        # if the word is a subject noun or an object noun
        if (token.pos_ == 'NOUN') or (token.pos_=='PROPN') and  (token.dep_ in ['dobj','pobj','nsubj','nsubjpass']):
            if token.text in headline:
#                 print(token.text, 'sample')
                # iterate over the children nodes
                for subtoken in token.children:
                    # if word is an adjective or has a compound dependency
                    if (subtoken.pos_ == 'ADJ') or (subtoken.dep_ == 'compound'):
                        phrase += subtoken.text + ' '

                if len(phrase)!=0:
                    phrase += token.text
            
             
        if  len(phrase)!=0:
            pat.append(phrase)
        
#     print(pat, length)
    return len(pat)/length
  
#person counts
def person_unique(text):
    d = {}
    
    doc = nlp(text)
    l =[ent.text for ent in doc.ents if ent.label_=='PERSON']
    for x in l:
        d[x] = d.get(x,0)+1
    c = 0
    for k,v in d.items():
        if v==1:
            c=c+1
    return c / len(l) if len(l) != 0 else 0


#person counts
def person_multiple(text):
    d = {}
    
    doc = nlp(text)
    l =[ent.text for ent in doc.ents if ent.label_=='PERSON']
    for x in l:
        d[x] = d.get(x,0)+1
    c = 0
    for k,v in d.items():
        if v!=1:
            c=c+1
    return c / len(l) if len(l) != 0 else 0

#org counts
def organisation_unique(text):
    d = {}
    
    doc = nlp(text)
    l =[ent.text for ent in doc.ents if ent.label_=='ORG']
    for x in l:
        d[x] = d.get(x,0)+1
    c = 0
    for k,v in d.items():
        if v==1:
            c=c+1
    return c / len(l) if len(l) != 0 else 0

#org counts
def organisation_multiple(text):
    d = {}
    
    doc = nlp(text)
    l =[ent.text for ent in doc.ents if ent.label_=='ORG']
    for x in l:
        d[x] = d.get(x,0)+1
    c = 0
    for k,v in d.items():
        if v!=1:
            c=c+1
    return c / len(l) if len(l) != 0 else 0

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__,prevent_initial_callbacks=True, external_stylesheets=external_stylesheets)


colors = {
    'text': '#33C3F0'
}
app.layout = html.Div(children=[
    html.H1(
        'Google',id='h1',
        style={
            "textAlign": "center",
            'backgroundColor': colors['text']
        }
    ),
    
    html.Div(dcc.Input(id='input-on-submit', type='text',placeholder ='Enter-url',style={
            'textAlign': 'center'
        } )),
    
    html.Button('Submit-1', id='submit-val-1', n_clicks=0, style={
            'textAlign': 'center',
            'color': '#D90416'
        }),
    html.Div(html.H6('story-type')),
    html.Div(id  ='story-type')

    
    

])

@app.callback(
    
    Output('story-type', 'children'),
    [Input('submit-val-1', 'n_clicks')],
    [State('input-on-submit','value')]
)

def update_graph(n_clicks,url):
    article = Article(str(url)) 
    article.download()
    article.parse()
    article.nlp()
    
    headline = article.title
    
    text = article.text
    
    text = clean(text)
    headline = clean(headline)
    
    text = replace_names(text)
    headline = replace_names(headline)

    score_1 = rule1(headline,text) # noun(subject), verb, noun(object) using headline and body
    score_2 = rule2(headline, text) # adjective using headline and body 
    score_3 = person_unique(text) # in body who appeared one times out of total person names list 
    score_4 = person_multiple(text) # in body who appeared more than one times out of total name
    score_5 = organisation_unique(text) # in body who appeared one times out of total name
    score_6 = organisation_multiple(text)# in body who appeared more than one times out of total name
    score_7 = headlines_person_unique(headline, text) # in body who appeared one times out of total name if that one also appeared in headlines
    score_8 = headlines_org_unique(headline, text) #in body who appeared one times out of total name, also that one also appeared in headlines
    score_9 = headlines_person_multiple(headline, text)# in body who appeared more than one times out of total name, also that one also appeared in headlines
    score_10 = headlines_org_multiple(headline, text) #in body who appeared more than one times out of total name if that one also appeared in headlines
    score_11 = len(sent_subtree(text))
    score_12 = len(sent_subtree_1(text))
    score_13 = len(double_quotes(headline, text))
#     score_11 = rule3(text)
    l = []
    if score_1>0.2:
        l.extend(['Standalone','Standalone','Standalone'])
    else:
        l.append('Industry-Based')
    if score_2>0.2:
        l.extend(['Standalone','Standalone','Standalone'])
    else:
        l.append('Industry-Based')
    if score_7<score_3:
        l.append('Industry-Based')
    else:
        l.append('Standalone')
    if score_8<score_5:
        l.append('Industry-Based')
    else:
        l.append('Standalone')
    if score_9>=score_4:
        l.append('Standalone')
    else:
        l.append('Industry-Based')
    if score_10>=score_6:
        l.append('Standalone')
    else:
        l.append('Industry-Based')
    if score_11>=score_12:
        l.append('Standalone')
    else:
        l.append('Industry-Based')
    if score_13>=1:
        l.append('Standalone')
    print(score_1, score_2,l,score_11,score_12, score_13)
    counter = Counter(l)
    max_count = max(counter.values())
    d = {}
    for x in l:
        d[x] = (l.count(x)/len(l))*100
    for k,v in d.items():
        print('{0} and its percentage is {1}'.format(k,v)) 
    return 'your story is {}'.format(*[item for item, count in counter.items() if count == max_count])
        
#     return score_1+score_2+score_3+score_4+score_5+score_7

if __name__ == "__main__":
    app.run_server(debug=True)
    
