import nltk
import clips
import itertools
import string

rules=["""
        (defrule learn_sentence_i_1
            ?a <- (sentence_i ?current ?next $?rest)
            (not(rule START ?current ?next))
            =>
            (assert (sentence ?current ?next $?rest))
            (assert (rule START ?current ?next))
            (retract ?a)
        )
        """,
       """
               (defrule learn_sentence_i_dup
                   ?a <- (sentence_i ?current ?next $?rest)
                   (rule START ?current ?next)
                   =>
                   (assert (sentence ?current ?next $?rest))
                   (retract ?a)

               )
               """,
       """
               (defrule learn_sentence_1
                   ?a <- (sentence ?previous ?current ?next $?rest)
                   (not(rule ?previous ?current ?next))
                   =>
                   (assert (sentence ?current ?next $?rest))
                   (assert (rule ?previous ?current ?next))
                   (retract ?a)
               )
               """,
       """
               (defrule learn_sentence_dup
                   ?a <- (sentence ?previous ?current ?next $?rest)
                   (rule ?previous ?current ?next)
                   =>
                   (assert (sentence ?current ?next $?rest))
                   (retract ?a)
               )
               """,
       """
               (defrule finish_learn_sentence_1
                   ?a <- (sentence ?previous ?current)
                   (not(rule ?previous ?current FINISH))
                   =>
                   (retract ?a)
                   (assert (rule ?previous ?current FINISH))
               )
               """,
       """
               (defrule finish_learn_sentence_dup
                   ?a <- (sentence ?previous ?current)
                   (rule ?previous ?current FINISH)
                   =>
                   (retract ?a)
               )""",
       """
               (defrule test_sen
                   (not(sentence $?))
                   (not(sentence_i $?))
                   (sentence_test_i $?)
                   =>
                   (assert (sentence_matched 0))
               )
               )""",
       """
               (defrule test_sentence_i
                   (not(sentence $?))
                   (not(sentence_i $?))
                   ?a <- (sentence_test_i ?current ?next $?rest)
                   (rule START ?current ?next)
                   (sentence_matched 0)
                   =>
                   (assert (sentence_test ?current ?next $?rest))
                   (retract ?a)
               )
               )""",
       """
               (defrule test_sentence_i_2
                   (not(sentence $?))
                   (not(sentence_i $?))
                   ?a <- (sentence_test_i ?current ?next $?rest)
                   (not(rule START ?current ?next))
                   (sentence_matched 0)
                   =>
                   (retract ?a)
               )
               )""",
       """
           (defrule test_sentence
               ?a <- (sentence_test ?previous ?current ?next $?rest)
               (rule ?previous ?current ?next)
               =>
               (assert (sentence_test ?current ?next $?rest))
               (retract ?a)
           )
           )""",
       """
           (defrule test_sentence_2
               ?a <- (sentence_test ?previous ?current ?next $?rest)
               (not(rule ?previous ?current ?next))
               =>
               (retract ?a)
           )
           )""",
       """
           (defrule finish_test_sentence
               ?a <- (sentence_test ?previous ?current)
               ?b <- (sentence_matched 0)
               (rule ?previous ?current FINISH)
               =>
               (assert (sentence_matched 1))
               (retract ?b)
               (retract ?a)
           )""",
       """
           (defrule finish_test_sentence_2
               ?a <- (sentence_test ?previous ?current)
               ?b <- (sentence_matched 0)
               (not(rule ?previous ?current FINISH))
               =>
               (retract ?a)
           )"""
       ]


def letter_generator():
    for iii in itertools.count(1):
        for p in itertools.product(string.ascii_uppercase, repeat=iii):
            yield ''.join(p)

def print_res(all_parsed,parsed,total_sentences,unparsed_sentences):
    if all_parsed:
        print("All sentences were parsed successfully.")
    else:
        print(str(parsed) + " from " + str(total_sentences) + " sentences were parsed.\n")
        print("The unparsed sentences are:")
        for sentence in unparsed_sentences:
            if sentence[len(sentence)-1] == "\n":
                print("    " + sentence[:-1])
            else:
                print("    " + sentence)

def check_pars(facts,env):
    parsed = 0
    total_sentences = len(facts)
    unparsed_sentences = []
    all_parsed = True
    for fact in facts:
        env.assert_string(fact)
        env.run()
        parsed_cond = True
        for fact1 in env.facts():
            if str(fact1).split("(")[1] == "sentence_matched 1)":
                parsed += 1
                fact1.retract()
            if str(fact1).split("(")[1] == "sentence_matched 0)":
                parsed_cond = False
                fact1.retract()
        if not parsed_cond:
            all_parsed = False
            index = facts.index(fact)
            f_in_tests = open("test.txt", 'r')
            for _ in range(index):
                f_in_tests.readline()
            unparsed_sentences.append(f_in_tests.readline())
    return parsed,all_parsed,total_sentences,unparsed_sentences

if __name__ == "__main__":
    env = clips.Environment()
    # first functionality
    f_in = open("train.txt", 'r')
    # input text
    text = ""
    for line in f_in:
        text += line
    # tokens into words
    tokens = nltk.word_tokenize(text)
    # parts of speech tagging
    tagged = nltk.pos_tag(tokens)
    # convert to clips facts
    facts = []
    template = "(sentence_i"
    sentence = template + " "
    for word in tagged:
        if word[1] == ".":
            sentence += ".)"
            facts.append(sentence)
            sentence = template + " "
        elif word[1] == "(" or word[1] == ")":
            continue
        else:
            sentence += word[1] + " "
    for fact in facts:
        env.assert_string(fact)
    # build all the rules
    for rule in rules:
        env.build(rule)
    # second functionality
    f_in_test = open("test.txt", 'r')
    # input text
    text = ""
    for line in f_in_test:
        text += line
    # tokens into words
    tokens = nltk.word_tokenize(text)
    # parts of speech tagging
    tagged = nltk.pos_tag(tokens)
    # convert to clips facts
    facts = []
    template = "(sentence_test_i"
    sentence = template + " "
    for word in tagged:
        if word[1] == ".":
            sentence += ".)"
            facts.append(sentence)
            sentence = template + " "
        elif word[1] == "(" or word[1] == ")":
            continue
        else:
            sentence += word[1] + " "
    # check if the sentences are parsed correctly
    parsed,all_parsed,total_sentences,unparsed_sentences = check_pars(facts,env)
    # print results
    print_res(all_parsed,parsed,total_sentences,unparsed_sentences)
