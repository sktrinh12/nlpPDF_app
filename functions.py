from nltk.stem import WordNetLemmatizer, PorterStemmer
import nltk
from models import *
import re
import os
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from spacy import displacy
from spacy.lang.en.stop_words import STOP_WORDS
import spacy

nlp = spacy.load("en_core_web_sm")
nlp_sci = spacy.load("en_core_sci_sm")
stopwords = nltk.corpus.stopwords.words('english')


lemmatiser = WordNetLemmatizer()
stemmer = PorterStemmer()
REGEX_PATTERN = re.compile(r'\w{3,}[. ]|[ ]\w|^\d+|\w{1,}\d+') #rid of molecular formulas or starts with numbers 

HTML_WRAPPER = """<div style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem">{}</div>"""

def allowed_file(filename):
    if not "." in filename:
        return False
    ext = filename.rsplit(".",1)[1]
    if ext.upper() in app.config['ALLOWED_FILE_EXT']:
        return True
    else:
        return False

def allowed_filesize(filesize):
    if int(filesize) <= app.config["MAX_FILESIZE"]:
        return True
    else:
        return False


def convert_chr(name):
	chr_list = []
	for l in name:
		chr_list.append(ord(l.lower()))
	return sum(chr_list)

def lemma_binary(word):
    '''
    Output overlapping words from a lemmatised word compared to the original word
    '''
    l_word = lemmatiser.lemmatize(word)
    word_lemma_dict = {'word_length' : len(word), 'lw_length' : len(l_word)}
    max_length = max(word_lemma_dict.values())
    longer_length_word = [k for k,v in word_lemma_dict.items() if v == max_length][0]
    for _ in range(max_length - word_lemma_dict['lw_length']):
        l_word += '0'
    binary_output = []
    for w,lw in zip(word,l_word):
        if w == lw:
            binary_output.append(1)
        else:
            binary_output.append(0)

    return binary_output.count(1)/len(binary_output)

def stem_compute(word):
    '''
    If the stem word account for more than 75% of the original word, it most likely is a name or species name
    '''
    stem_dict = {}
    stem_dict['s_word'] = stemmer.stem(word)
    stem_dict['word_length'] = len(word)
    stem_dict['stem_length'] = len(stem_dict['s_word'])
    stem_dict['ratio'] = stem_dict['stem_length'] / stem_dict['word_length']
    if stem_dict['ratio'] > .75:
        stem_dict['output'] = 1
    else:
        stem_dict['output'] = 0
    return stem_dict

def last_char(word):
    try:
        return word[-2:]
    except IndexError:
        return word[-1]

def first_char(word):
    try:
        return word[:2]
    except IndexError:
        return word[0]

def find_features(word):
    return {'word_length':len(word),\
            'last_letters':last_char(word),\
            'first_letters':first_char(word),\
            'lemma':lemma_binary(word),\
            'stem':stem_compute(word)['output'],\
            'convert_chr':convert_chr(word)
            }

def update_stopw(nlp):
    for e in ").,-~%;:(/@! &*#`":
        nlp.vocab[e].is_stop = True
    print(f'updated stop words for {nlp} !')

#update new stop words
update_stopw(nlp)
update_stopw(nlp_sci)

class VoteClassifier(ClassifierI):
    def __init__(self, classifiers): #list of classifiers
        self._classifiers_dict = classifiers

    def clf_name(self): #list all the classifer names
        return list(self._classifiers_dict.keys())

    def classify(self, string_features):
        votes = []
        for c in self._classifiers_dict.values(): #the 8 diff algorithms
            v = c.classify(find_features(string_features.lower())) #either True or False
            votes.append(v)
        try:
            res = mode(votes)
        except StatisticsError as e:
            res = True #if equal number of True's and False, just set to True
        return res #return value (boolean)

    def confidence(self, string_features):
        #count how many were in 'True' using the 8 different algorithms
        votes = []
        for c in self._classifiers_dict.values():
            v = c.classify(find_features(string_features.lower()))
            votes.append(v)
        try:
            choice_votes = votes.count(mode(votes)) #count the amt of True's or False's
        except StatisticsError as e:
            choice_votes = len(votes)/2 #should be 4 since half
        conf = choice_votes / len(votes) #how many out of the 8 were True or False
        return conf

def vote_clf():
    '''
    Load the trained or pre-trained pickled algorithm
    returns the voted classifier dictionary
    '''
    wd = cwd + '/models/'
    clfs = ['K Nearest Neighbors',
            'Decision Tree',
            'Random Forest',
            'Logistic Regression',
            'SGD Classifier',
            'Multinomial',
            'Bernoulli',
            'LinearSVC',
            'ComplementNB']
    classifiers_models = {}
    for clf_n in clfs:
        with open(f'{wd}{clf_n}.pickle', 'rb') as clf_file:
            classifiers_models[clf_n] = pickle.load(clf_file)
    voted_classifier = VoteClassifier(classifiers_models)
    return voted_classifier

def check_if_name_related(q_word,verbose=False):
    return_result = {}
    return_result['Classification'] = voted_classifier.classify(q_word)
    return_result['Confidence'] = voted_classifier.confidence(q_word)*100
    if verbose:
        print(f"Classification: {return_result['Classification']} Confidence: {return_result['Confidence']}", )
    return return_result['Classification']

voted_classifier = vote_clf()

#load raw pdf text
def load_text(filepath):
    with open(filepath, 'r') as f:
        read_output = f.readlines()
    read_output = '\n'.join(read_output).strip().replace('\n','')
    if os.path.exists(filepath): #after reading in the text and saving to var, delete file to tidy
        os.remove(filepath)
    return read_output

def filter_text_stopw(pdf_text):
    '''
    filter text based on stop words; regular english web
    '''
    token_list = []
    for token in pdf_text:
        token_list.append(token.text)

    filtered_pdf =[]
    for word in token_list:
        lexeme = nlp.vocab[word]
        if lexeme.is_stop == False:
            filtered_pdf.append(word)
    return filtered_pdf

def filter_text_pos(pdf_pt,types_of_pos=['NN', 'NNS', 'VBN', 'NNP', 'JJ', 'VBZ']):
    '''
    filter text based on part of speech tag
    '''
    try:
        filtered_nnp = []
        for pt in pdf_pt:
            q_str = str(pt[1])
            if pt[2] in types_of_pos and '-' not in q_str and len(q_str) > 5:
                    filtered_nnp.append(pt)
    except IndexError as e:
        pass #last index doesn't have a neighbour
    return filtered_nnp

def output_display(f_pdf, f_pdfsci):
    out_dply_set_en = set()
    out_dply_set_sci = set()
    out_dply_ls_en = []
    out_dply_ls_sci = []

    try:
        for i in f_pdfsci:
            string_word = rm_spec_char(str(i[1]).lower())
            if not re.search(REGEX_PATTERN,string_word):
                if string_word not in out_dply_set_sci:
                    out_dply_ls_sci.append(str(i[1]))
                out_dply_set_sci.add(string_word)
        for j in f_pdf:
            string_word = rm_spec_char(str(j[1]).lower())
            res = check_if_name_related(string_word)
            if res and not re.search(REGEX_PATTERN,string_word):
                if string_word not in out_dply_set_en:
                    out_dply_ls_en.append(str(j[1]))
                out_dply_set_en.add(string_word)
    except TypeError as e:
        pass

    return (' '.join(out_dply_ls_sci), \
            ' '.join(out_dply_ls_en))

def dplcy_sci(output_dply, title):
    pdf_o = nlp_sci(output_dply)
    #set titles and colours, options
    pdf_o.user_data["title"] = title
    colours = {"ENTITY" : '#e6efff'}
    options = {"ents": ["ENTITY"], "colors": colours}
    html = displacy.render(pdf_o, style='ent', options = options)
    return html

def dplcy_en(output_dply, title, POS_type):
    pdf_o = nlp(output_dply)
    #set titles and colours, options
    pdf_o.user_data["title"] = title
    colours = {POS_type : '#e6efff'}
    options = {"ents": [POS_type], "colors": colours}
    html = displacy.render(pdf_o, style='ent', options = options)
    return html

def rm_spec_char(string):
    #rid of strange chars
    return ''.join(' ' if not e.isalnum() else e for e in string.strip())

def format_html(html):
    html = html.replace("\n\n","\n")
    return HTML_WRAPPER.format(html) #adjust border and style

def tokenize_render(filepath, title_sci, title_en, POS_type):
    read_output = load_text(filepath)
    pdf_o = nlp(read_output) #tokenize based on regular eng words
    pdf_osci = nlp_sci(read_output) #tokenize based on scientific words
    f_pdf_o = nlp(' '.join(filter_text_stopw(pdf_o))) #filter stop words then tag it again
    f_pdf_osci = nlp_sci(' '.join(filter_text_stopw(pdf_osci)))
    pdf_pt = [(n, i, i.tag_) for n,i in enumerate(f_pdf_o)]
    pdf_ptsci = [(n, i, i.tag_) for n,i in enumerate(f_pdf_osci)] #part of speech tags
    f2_pdf_sci = filter_text_pos(pdf_ptsci,['NN', 'NNS', 'VBN', 'NNP'])
    f2_pdf = filter_text_pos(pdf_pt) #use of default POS tag list
    sci_output, en_output = output_display(f2_pdf, f2_pdf_sci)
    # print(sci_output)
    # print(en_output)
    return format_html(dplcy_sci(sci_output, title_sci)), format_html(dplcy_en(en_output, title_en, POS_type))
