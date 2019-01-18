def get_message(temp):

    start = temp.find("text")+8
    temp1 = temp[start:]
    end = temp1.find(",")
    return temp[start:start+end-1]


def write_to_a_file(filename, data):

    with open(filename,"w", encoding='utf-8') as writer:
        for x in data:
            writer.write(str(x)+'\n')