def extract_entities(filename):
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

    ##### Загружаем txt файл для разметки

    #INPUT_FILENAME = 'anna-karenina.txt'
    INPUT_FILENAME = filename
    text = ''
    with open(INPUT_FILENAME, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:      
            text += line

    ##### Используем предобучение модели из библиотеки Natasha

    navec = Navec.load('navec_news_v1_1B_250K_300d_100q.tar')
    ner = NER.load('slovnet_ner_news_v1.tar')
    ner.navec(navec)

    ##### Подключаем функцию сегментации текста

    segmenter = Segmenter()
    doc = Doc(text)
    doc.segment(segmenter)

    named_triplets = [] # тут будет список словарей

    


    ##### Извлекаем именованные сущности из каждого предложения, формируем общий список триплетов (словарей)

    sents = list(segmenter.sentenize(text))

    for sent in sents:
        markup = ner(sent.text)
        if len(markup.spans):
            for i in range(len(markup.spans)):
                triplet_dict = {
                    'type':markup.spans[i].type, 
                    'name':markup.text[markup.spans[i].start:markup.spans[i].stop], 
                    'context':markup.text
                }
                named_triplets.append(triplet_dict)


    #named_triplets







    ##### Лемматизация name для каждого триплета

    morph = pymorphy2.MorphAnalyzer() # для лемматизации

    # функция лемматизации
    def lemmatize(name):
        words = name.split() # разбиваем текст на слова
        res = list()
        for word in words:
            p = morph.parse(word)[0]
            res.append(p.normal_form)

        return res

    for i in range(len(named_triplets)):
        p = lemmatize(named_triplets[i].get('name'))
        named_triplets[i].update({'name': p[0]})

    #named_triplets

    ##### Удаляем дубликаты триплетов, формируем множество

    unic_names = set()
    for i in range(len(named_triplets)):
        if named_triplets[i].get('name') in unic_names:
            continue
        else:
            unic_names.add(named_triplets[i].get('name'))

    #unic_names

    ##### творим магию-хуягию

    # составим список количесва вхождений каждой уникальной сущности для того, чтобы потом оставить по три предложения для каждого
    count_named_triplets = list()
    for name in unic_names:
        quantity = 0
        for  i in range(len(named_triplets)):
            if name == named_triplets[i].get('name'):
                quantity += 1
        d = {'name': name, 'quantity': quantity}
        count_named_triplets.append(d)

    #count_named_triplets

    ##### Составляем финальный список триплетов, содержащий уникальные имена и контекст не более трех предложений из текста

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
            
            

    #unic_named_triplets



    ##### Формируем итоговый json файл, кладем туда список триплетов - unic_named_triplets

    
    # JSON_string = json.dumps(unic_named_triplets, ensure_ascii=False, indent=4).encode('utf8')

    # filename = "anna-karenina.json"
    # with open(filename, 'w') as file_object:
    #     file_object.write(JSON_string.decode())

    

    return unic_named_triplets

print(extract_entities('test.txt'))

