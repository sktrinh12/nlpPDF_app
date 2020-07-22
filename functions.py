from nltk.stem import PorterStemmer #WordNetLemmatizer
from models import *
from collections import defaultdict # to get unique values in list
import re
import os
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.corpus import stopwords
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from io import BytesIO

stop_words_list = stopwords.words('english')

stemmer = PorterStemmer()
REGEX_PATTERN = re.compile(r'\w{3,}[. ]|[ ]\w|^\d+|\w{1,}\d+') #rid of molecular formulas or starts with numbers 

HTML_WRAPPER = """<div style="overflow-x: auto; border: 0.75px solid #e6e9ef; border-radius: 0.25rem; padding: 0.75rem">{}</div>"""


def calc_weights():
    '''
        scores obtained from running accuracy score from nbk, will return dictionary of
        weighted percentage of each clf based on its rank (rank centroid)
    '''
    scores = {
        'linsvc': 0.802,
        'sgd':  0.779,
        'knn' : 0.835,
        'logreg' : 0.801,
        'rf' : 0.849,
        'bern' :0.731
        }
    # calculate the Rank order centroid; these weighting values are higher 
    weights = {k : 0 for k in scores.keys()}
    K = len(voted_classifier_dict)
    # sort the scores by value x[1] index and use the enumerable as j
    for i,(mdl, scr) in enumerate(sorted(scores.items(), key=lambda x: x[1], reverse=True)):
        weights[mdl] = 1/K * sum([1/j for j in range(i+1,len(scores)+1)])
    return weights

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

# cleaning function for science words
def filter_nonchar(paragraph_list):
    """if any non-char is present or numeric and not a stop word and length > 3 and excludes ATGC nucleic acids strings"""
    return [s for s in paragraph_list if not re.search(r'[\W+\d+]', s) and \
            s not in stop_words_list and \
            len(s) > 3 and \
            re.search(r'[^ATCG]', s)]

# function to format the features into a column to prepare for making into np array and easily predict usign clf 
def format_feats_into_df(word):
    df = pd.DataFrame(find_features(word).items()).transpose()
    df.columns = df.iloc[0].copy()
    df = convert_to_binary(df)
    df.drop([0], inplace=True)
    return df.iloc[0]

# function to convert the strings to binary in order to input into machine learning algos 
def convert_to_binary(df):
    """convert the first and last letters to binary"""
    for i in range(1,3):
        df[f'last_letters_{i}'] = df[f'last_letters_{i}'].apply(lambda x: ''.join(format(ord(w), 'b') for w in x) )
        df[f'first_letters_{i}'] = df[f'first_letters_{i}'].apply(lambda x: ''.join(format(ord(w), 'b') for w in x) )
    return df

vowels = "aeiouyAEIOUY"

def calc_vowels_consonants_syllable(word):
    word = word.lower()
    SYLLABLE = 0
    VOWELS = 0
    CONSONANTS = 0
    if word[0] in vowels:
        SYLLABLE += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            SYLLABLE += 1
        if word[index] in vowels:
            VOWELS += 1
        else:
            CONSONANTS += 1
    if word.endswith("e"):
        SYLLABLE -= 1
    if SYLLABLE == 0:
        SYLLABLE += 1
    return VOWELS, CONSONANTS, SYLLABLE

def stem_compute(word):
    '''
    Output ratio of stem word to original word
    '''
    s_word = stemmer.stem(word)
    word_length = len(word)
    stem_length = len(s_word)
    try:
        ratio = stem_length / word_length
    except ZeroDivisionError:
        ratio = 1
    return ratio

def last_char(word):
    '''
    Extract the last three characters of the word
    '''
    return word[-3:]

def first_char(word):
    '''
    Extract the first two characters of the word
    '''
    return word[:3]

def preprocess_word(word):
    processed_word = re.sub(r'[^A-Za-z-]', '', word) # remove special chars
    return processed_word

def find_features(two_words):
    '''
    feature extraction and store into dictionary for training
    '''
    word_dict = {}
    for i,w in enumerate(two_words.split(' ')):
        if i == 0: # lowercase and captailize first letter of first word
            w = w.lower().capitalize()
        else:
            w = w.lower()
        n_vowels, n_consonants, n_syllables = calc_vowels_consonants_syllable(w)
        word_dict[i] = {
                                'word': preprocess_word(w),
                                'n_vowels' : n_vowels,
                                'n_consonants' : n_consonants,
                                'n_syllables' : n_syllables,
                                'word_length' : len(w)
                        }

        try:
            word_dict[i]['ratio_vow_con']  = n_vowels/n_consonants
        except ZeroDivisionError:
            word_dict[i]['ratio_vow_con'] = 1

        try:
            word_dict[i]['ratio_vow_syl'] = n_vowels/n_syllables
        except ZeroDivisionError:
            word_dict[i]['ratio_vow_syl'] = 1

    f_char_1 = first_char(word_dict[0]['word'])
    f_char_2 = first_char(word_dict[1]['word'])
    l_char_1 = last_char(word_dict[0]['word'])
    l_char_2 = last_char(word_dict[1]['word'])

    return {'word_length_1': word_dict[0]['word_length'],\
            'word_length_2': word_dict[1]['word_length'],\
            'last_letters_1': l_char_1,\
            'last_letters_2': l_char_2,\
            'first_letters_1': f_char_1,\
            'first_letters_2': f_char_2,\
            'stem_1':stem_compute(word_dict[0]['word']),\
            'stem_2':stem_compute(word_dict[1]['word']),\
            'vowel_ratio_1':word_dict[0]['n_vowels']/word_dict[0]['word_length'],\
            'vowel_ratio_2':word_dict[1]['n_vowels']/word_dict[1]['word_length'],\
            'consonant_ratio_1':word_dict[0]['n_consonants']/word_dict[0]['word_length'],\
            'consonant_ratio_2':word_dict[1]['n_consonants']/word_dict[1]['word_length'],\
            'syllable_ratio_1':word_dict[0]['n_syllables']/word_dict[0]['word_length'], \
            'syllable_ratio_2':word_dict[1]['n_syllables']/word_dict[1]['word_length'], \
            'ratio_vow_con_1': word_dict[0]['ratio_vow_con'],\
            'ratio_vow_con_2': word_dict[1]['ratio_vow_con'],\
            'ratio_vow_syl_1': word_dict[0]['ratio_vow_syl'],\
            'ratio_vow_syl_2': word_dict[1]['ratio_vow_syl']
           }


class VoteClassifier(object):
    def __init__(self, classifiers, weights=None): #list of classifiers
        self._classifiers_dict = classifiers
        self._weights = weights

    def clf_name(self): #list all the classifer names
        return list(self._classifiers_dict.keys())

    def calc_weighted_choice(self, votes):
        """calculate the weighted True's and Falses's based on the weights passed in as an argument"""
        trues_ = []
        falses_ = []
        for i_, (k_,v_) in enumerate(votes.items()):
            # if the value is True
            if v_:
                trues_.append(weights[k_])
            else:
                falses_.append(weights[k_])

        return { True: sum(trues_), False: sum(falses_) }

    def classify(self, word):
        """classify the string word (as True or False) based on pre-defined weights or equal weights"""
        votes = {}
        for mdl, clf in self._classifiers_dict.items(): #the number of diff algorithms
            #either True or False; returns a list of one element, so just index it
            votes[mdl] = clf.predict(np.array(format_feats_into_df(word)).reshape(1,-1))[0]

        if weights:
            # return the key of the max value based on (weighted) value
            tmp_dict = self.calc_weighted_choice(votes)
            print('%True: {:.2f}; %False: {:.2f}'.format(*list( tmp_dict.values() ) ) )
            return max(tmp_dict.items(), key=operator.itemgetter(1))[0]

        # if no weights supplied just use equal weights for all clfs
        else:
            try:
                return mode(votes)
            except StatisticsError as e:
                return True #if equal number of True's and False, just set to True

    def confidence(self, word):
        #count how many were in 'True' using the 8 different algorithms
        votes = []
        for clf in self._classifiers_dict.values():
            result = clf.predict(np.array(format_feats_into_df(word)).reshape(1,-1))[0]
            votes.append(result)
        try:
            choice_votes = votes.count(mode(votes)) #count the amt of True's or False's
        except StatisticsError as e:
            choice_votes = len(votes)/2 # if even split then should be half/half True/False; just divide by 2
        conf = choice_votes / len(votes) #how many out of the 8 were True or False
        return conf

def vote_clf():
    '''
    Load the trained or pre-trained pickled algorithm
    returns the voted classifier dictionary
    '''
    wd = cwd + '/models/'
    classifiers_models = {}
    for fi in os.listdir(wd):
        if 'taxon_names' in fi and fi.endswith('pkl'):
            model_name = fi.split('_')[0]
            with open(os.path.join(wd, fi), "rb" ) as pkl_fi:
                classifiers_models[model_name] = joblib.load(pkl_fi)
    return classifiers_models

# def check_if_name_related(q_word,verbose=False):
#     return_result = {}
#     return_result['Classification'] = voted_classifier.classify(q_word)
#     return_result['Confidence'] = voted_classifier.confidence(q_word)*100
#     if verbose:
#         print(f"Classification: {return_result['Classification']} Confidence: {return_result['Confidence']}", )
#     return return_result['Classification']

# load the pickle models from file and save into dictionary
voted_classifier_dict = vote_clf()
# calculate the weights based on ranks
weights = calc_weights()
# instaniate the vote class passing the weights
voted_classifier = VoteClassifier(voted_classifier_dict, weights)

def load_text(load_input): #just read raw text form or from pdf
    if load_input.endswith('.txt'): # just load from text
        with open(load_input, 'r') as f:
            text_body = f.readlines()
    else: # load body of text after pdfminer
        text_body = pdf_parse(load_input)
    read_output = '\n'.join(text_body).strip().replace('\n','')
    return read_output

def rm_file(filepath):
    if os.path.exists(filepath): #after reading in the text and saving to var, delete file to tidy
        os.remove(filepath)

def filter_text_pos(pdf_pt):
    '''
    filter text based on part of speech tag and neighbouring characteristics
    '''
    filtered_nnp = []
    for i,pt in enumerate(pdf_pt):
        # if noun type tag
        if pt[1] in ["NNP", "NN"]:
            try:
                # if the neighbour is also a noun-type tag
                if pdf_pt[i+1][1] in ["NNP", "NN"]:
                    # if the neighbouring word is lowercase or uppercase
                    if pdf_pt[i+1][0].islower() or pdf_pt[i+1][0].isupper():
                        # if the first letter of the first word is uppercase
                        if pt[0][0].isupper(): # if first letter is capitalised 
                            # append the word pair 
                            filtered_nnp.append(f'{pt[0]} {pdf_pt[i+1][0]}' )

            except IndexError:
                pass # last index doesn't have a neighbour
    return filtered_nnp

def rtn_possible_wp(vc, pdf_pt):
    '''
       returns possible word pairs that the classifier deeemed as a taxonomy name;
       it is not that smart; requires a VoteClassifer object, and the filtered
       text list with part of speech tagging
    '''
    possible_list = []
    for wp in filter_text_pos(pdf_pt):
        res = vc.classify(wp)
        if res:
            possible_list.append(wp)
    if possible_list:
        return list(defaultdict.fromkeys(possible_list).keys())
    return ["Sorry, failed to find taxonomy-like names in the document"]


# def format_html(html):
#     html = html.replace("\n\n","\n")
#     return HTML_WRAPPER.format(html) #adjust border and style

def tokenise_render_v2(filepath):
    text_body = load_text(filepath)
    if text_body:
        rm_file(filepath) #clean up file in static folder
    token_pdf = word_tokenize(text_body)
    filtered_pdf = filter_nonchar([w for w in token_pdf if not w in stop_words_list])
    pdf_pt = pos_tag(filtered_pdf)
    poss_wp = rtn_possible_wp(voted_classifier, pdf_pt)
    poss_nscs = extract_nsc(text_body)
    return poss_wp, poss_nscs

def pdf_parse(filepath):
    manager = PDFResourceManager()
    retstr = BytesIO()
    layout = LAParams(all_texts=True)
    device = TextConverter(manager, retstr, laparams=layout)
    with open(filepath, 'rb') as pdf_file:
        interpreter = PDFPageInterpreter(manager, device)
        for page in PDFPage.get_pages(pdf_file, check_extractable=True):
            interpreter.process_page(page)

        text = retstr.getvalue()
        device.close()
        retstr.close()
    return text.decode('utf-8')

def nsc_exclude(ls_vouch_nsc):
    if isinstance(ls_vouch_nsc, list):
        res_list = []
        for n in ls_vouch_nsc:
            if 'C' in n and 'H' in n:
                pass
            else:
                res_list.append(n)
    else:
        res_list = ls_vouch_nsc
    return res_list

def extract_nsc(text_body):
    # vouch_nsc = re.findall(r'(^[JCNQFM]{1}\w{1,}\d{2,})', text_body)
    vouch_nsc = re.findall(r'([J|C|N|Q|F|M]{1}\d{2,}\w+)', text_body)
    # vouch_nsc = re.findall(r'([^ABD-IK-LO-PR-Zabd-ik-lo-pr-z]\w+\d{2,})', text_body)
    try:
        vouch_nsc = [r for r in vouch_nsc if len(r) < 10 and len(r) > 4]
    except:
        vouch_nsc = ["Didn't find any NSCs"]
    print(vouch_nsc)
    if len(vouch_nsc) > 1:
        vouch_nsc = nsc_exclude(vouch_nsc)
        if not vouch_nsc:
            # if after removing CH formulas and the list becomes empty
            return ["Didn't find any NSCs"]
        vouch_nsc = list(defaultdict.fromkeys(vouch_nsc).keys())
    else:
        if vouch_nsc:
            # if just one found
            vouch_nsc = vouch_nsc
        else:
            vouch_nsc = ["Didn't find any NSCs"]
    return vouch_nsc
