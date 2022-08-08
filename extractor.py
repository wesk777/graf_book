# Анна Каренина Л. Н. Толстой (версия 1) 

### Извлекаем именованные сущности: Имена, Места, Названия, с помощью библиотек navec и slovnet
#### Формируем json файл с триплетами: type: PER/LOC/ORG, name, context.

##### Установка необходимых библиотек

# pip install slovnet
# pip install ipymarkup
# pip install pymorphy2
# pip install natasha
# import json

    

from navec import Navec
from slovnet import NER
from ipymarkup import show_span_ascii_markup as show_markup
import pymorphy2
from natasha import Segmenter, Doc
import logging


MORPH = pymorphy2.MorphAnalyzer()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def read_file(filename: str) -> str: #файл в формате txt  # ВОТ ТУТ ВОПРОСИКИ ?????????????

    text = ''
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:      
            text += line    
    logger.info('-----------------------------Файл прочитал---------------------------------------')
    return text

# Лемматизация слова
def lemmatization_of_word(text: str) -> str:
    words = text.split() # разбиваем текст на слова, например Облонского Степана Аркадьича -> облонский степан аркадьевич
    res = list()
    for word in words:
        p = MORPH.parse(word)[0]
        res.append(p.normal_form) # наверное можно сразу строку возвращать, чтобы в триплете не преобразовывать

    return ' '.join(res)



def segmentation_text(text: str) -> list[dict]:
    '''
    Сегментация текста на предложения
    Используем предобучение модели из библиотеки Natasha
    Извлекаем именованные сущности из каждого предложения, формируем общий список триплетов (словарей)
    '''
    segmenter = Segmenter()
    doc = Doc(text)
    doc.segment(segmenter)
    
    navec = Navec.load('navec_news_v1_1B_250K_300d_100q.tar')
    ner = NER.load('slovnet_ner_news_v1.tar')
    ner.navec(navec)


    sents = list(segmenter.sentenize(text))
    named_triplets = [] # тут будет список словарей
    for sent in sents:
        markup = ner(sent.text)
        if  not markup.spans:
            continue
        for i in range(len(markup.spans)):
            start = markup.spans[i].start
            stop = markup.spans[i].stop
            list_lemmatized_names = lemmatization_of_word(markup.text[start:stop]) 
            triplet_dict = {
                'type':markup.spans[i].type, 
                'name': list_lemmatized_names,
                'context':markup.text
            }
            named_triplets.append(triplet_dict)
    logger.info('-----------------------Сегментацию и лемматизацию выполнил-----------------------')
    return named_triplets



def delete_repeatable_entities(named_triplets: list[str]) -> set:
    '''
    Удаляем дубликаты триплетов
    Формируем множество уникальных именованных сущностей
    '''
    unic_names = set()
    for i in range(len(named_triplets)):
        name = named_triplets[i].get('name')
        if name not in unic_names:
            unic_names.add(name)
            
    logger.info('----------------------------Удалил дубликаты-------------------------------------')
    return unic_names      



def count_quantity_of_entities(unic_names: set, named_triplets: list[dict]) -> list[dict]:
    '''
    составим список количесва вхождений каждой уникальной сущности для того, 
    чтобы потом оставить по три предложения для каждого
    '''
 
    count_named_triplets = list()
    for name in unic_names:
        quantity = 0
        for  i in range(len(named_triplets)):
            if name == named_triplets[i].get('name'):
                quantity += 1
        d = {
            'name': name, 
            'quantity': quantity
            }
        count_named_triplets.append(d)
    logger.info('---------------Подсчитал количество вхождений именованных сущностей--------------')
    
    return count_named_triplets


def create_named_entities(count_named_triplets: list[dict], named_triplets: list[dict]) -> list[dict]:
    '''
    Составляем финальный список триплетов, содержащий уникальные имена и контекст не более трех предложений из текста
    '''

    unic_named_triplets = list()

    for i in range(len(count_named_triplets)):
        if count_named_triplets[i].get('quantity') > 3:
            flag = 0
            context = list()
            for j in range(len(named_triplets)):
                if flag == 3:
                    break
                
                if named_triplets[j].get('name') == count_named_triplets[i].get('name'):
                    type_i = named_triplets[j].get('type')
                    name = named_triplets[j].get('name')
                    if ' '.join(context) != named_triplets[j].get('context'):
                        context.append(named_triplets[j].get('context'))
                    flag += 1
        else:
            context = list()
            for j in range(len(named_triplets)):
                if named_triplets[j].get('name') == count_named_triplets[i].get('name'):
                    type_i = named_triplets[j].get('type')
                    name = named_triplets[j].get('name')
                    if ' '.join(context) != named_triplets[j].get('context'):
                        context.append(named_triplets[j].get('context'))
        
        
        triplet_dict = {
                    'type':type_i, 
                    'name':name, 
                    'context':context
                }
        unic_named_triplets.append(triplet_dict)
    logger.info('---------------------------Собрал именованные сущности---------------------------')  
    return unic_named_triplets





def index(text: str) -> list[dict]:
    named_triplets: list[str] = segmentation_text(text)    
    # named_triplets_lemmatized: list[dict] = lemmatization(named_triplets)
    unic_names: set = delete_repeatable_entities(named_triplets)
    count_named_triplets: list[dict] = count_quantity_of_entities(unic_names, named_triplets)
    unic_named_triplets: list[dict] = create_named_entities(count_named_triplets, named_triplets)
    return unic_named_triplets




logger.info('--------------------------------------СТАРТ--------------------------------------')          
INPUT_FILENAME = 'anna-karenina.txt'
#INPUT_FILENAME = 'test.txt'
text: str = read_file(INPUT_FILENAME)
index(text)
logger.info('--------------------------------------КОНЕЦ--------------------------------------')



