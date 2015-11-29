#Function to put in memory conf file in hash format
def putInMem(hashT):
    file1 = open("conf.txt")
    for i in file1:
        aux = i.split('|')
        ID = aux[0]
        NAME = aux[1].strip('\n')
        hashT.append((ID,NAME))

#Function to see if a movie is in hash
def haveInHash(name, hashT):
    print '**************************************************************'
    print 'ID list'
    for i in range(0, len(hashT)):
        if name in hashT[i]:
            print "ID: ", hashT[i][0]

#Function to split hash
def divide(hashT):
    print '**************************************************************'
    print 'HASH NODE SON'
    hashToReturn = []
    for i in range(len(hashT)/2, len(hashT)):
        hashToReturn.append(hashT[i])
            
    print hashToReturn
    return hashToReturn

def main():
    import os
    os.system('clear')
    hashT = []
    putInMem(hashT)
    print '**************************************************************'
    print "HASH NODE ROOT"
    print hashT
    name = 'name1'
    haveInHash(name, hashT)
    hashT = divide(hashT)
    hashT = divide(hashT)

if __name__ == "__main__":
    main()
