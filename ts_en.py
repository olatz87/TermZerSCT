import nltk,codecs,json,optparse,sys,re,glob
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer, SimpleJSONRPCRequestHandler
from util.klaseak import *

class HierarkiakKargatu:     
    def __init__(self,inp):
        # self.hierarkiak = {}
        # Hierarkia = ["CLINICAL_DIS","CLINICAL_FIN","BODYSTRUCTURE","ENVIRONMENT","EVENT","FORCE","OBJECT","OBSERVABLE","ORGANISM","PHARMPRODUCT","PROCEDURE","QUALIFIER","RECORD","SITUATION","SOCIAL","SPECIAL","SPECIMEN","STAGING","SUBSTANCE"]
        # for hie in Hierarkia:
        #     for syn in ["_pre_eng.txt",'_syn_eng.txt']:
        #         f = '../../../euSnomed/snomed/hierarkiak/'+hie+syn
        #         print(f,"kargatzen...")
        #         with codecs.open(f,encoding='utf-8') as fitx:
        #             for line in fitx:
        #                 desk = " ".join(nltk.word_tokenize(line.strip().split('\t')[7].lower()))
        #                 if desk in self.hierarkiak:
        #                     lag = self.hierarkiak[desk]
        #                     if hie not in lag:
        #                         self.hierarkiak[desk] = lag + '#' + hie
        #                 else:
        #                     self.hierarkiak[desk] = hie

        m = re.match('.*/SnomedCT_RF([12])Release_([^_]*)_([^/]*)/',inp)
        if m:
            rf = m.group(1)
            fileType = "sct"+rf
            namespace = m.group(2)
            version = m.group(3)
            if rf == "1":
                path = "Terminology/Content/"
                dist = "Core"
            else:
                dist = "Snapshot"
                path = dist+"/Terminology/"
                pathL = dist+"/Refset/Language/"
                fileTypeL = "der"+rf

        else:
            print('fitxategiaren izena ez da ezagutu')
            exit()
        print(inp+path)
        fitxC = glob.glob(inp+path+'*_Concept*.txt')[0]
        fitxD = glob.glob(inp+path+'*_Description*.txt')[0]
        fitxR = glob.glob(inp+path+'*_Relationship*.txt')[0]
        self.lanZer = {}
        if rf == "2":
            fitxL = glob.glob(inp+pathL+'*Language*.txt')[0]
            self.lanZer = LanguageList(fitxL)
            print("Language kargatuta",len(self.lanZer.zerrenda))
        self.konZer = ConceptList(fitxC)
        print("Kontzeptuak kargatuta",len(self.konZer.zerrenda))
        self.desZer = DescriptionList(fitxD,self.konZer,self.lanZer)
        print("Deskribapenak kargatuta",len(self.desZer.zerrenda))
        self.erlZer = RelationshipList(fitxR,self.konZer,True)
        print("Erlazioak kargatuta",len(self.erlZer.umeZerrenda))
        self.erlZer.hierarkiakEsleitu()
        print("Hierarkiak kargatuta",len(self.erlZer.hierarkiak))


    def deskribapenakJaso(self):
        return json.dumps(self.desZer.zerrendaLortu(),ensure_ascii=False)

    def deskribapenArabera(self):
        return json.dumps(self.desZer.deskribapenArabera(),ensure_ascii=False)

    def sct2term(self,sctId):
        return json.dumps(self.konZer.sct2term(sctId),ensure_ascii=False)

    def sct2desc(self,sctId):
        return json.dumps(self.konZer.sct2desc(sctId),ensure_ascii=False)

    def sct2hierarkiak(self,sctId):
        return json.dumps(self.erlZer.hierarkiaLortu(sctId),ensure_ascii=False)

    def desc2sct(self,desc,lemma):
        return json.dumps(self.desZer.kodeaLortu(desc,lemma),ensure_ascii=False)
        
    def kontzeptuakJaso(self):
        return json.dumps(self.konZer.zerrendaLortu(),ensure_ascii=False)

    def kontzeptuaJaso(self,sctId):
        return json.dumps(self.konZer.kontzeptua(sctId),ensure_ascii=False)

    def dId2desc(self,dId):
        return json.dumps(self.desZer.dId2desc(dId),ensure_ascii=False)

def main():
    """
    The code below starts an JSONRPC server
    """
    parser = optparse.OptionParser(usage="%prog [OPTIONS]")
    parser.add_option('-p', '--port', default='9602',
                      help='Port to serve on (default 9602)')
    parser.add_option('-H', '--host', default='158.227.106.115',
                      help='Host to serve on (default siuc06; 0.0.0.0 to make public)')
    parser.add_option('-v', '--verbose', action='store_false', default=False, dest='verbose',
                      help="Quiet mode, don't print status msgs to stdout")
    options, args = parser.parse_args()
    VERBOSE = options.verbose
    # server = jsonrpc.Server(jsonrpc.JsonRpc20(),
    #                         jsonrpc.TransportTcpIp(addr=(options.host, int(options.port))))
    try:
        #rh = AllPathRequestHandler if options.ignorepath else SimpleJSONRPCRequestHandler
        rh = SimpleJSONRPCRequestHandler
        server = SimpleJSONRPCServer((options.host, int(options.port)),
                                     requestHandler=rh)
        inp = '/sc01a7/users/ixamed/BaliabideSemantikoak/SnomedCT_RF2Release_INT_20150731/'
        des = HierarkiakKargatu(inp)
        server.register_function(des.deskribapenakJaso)
        server.register_function(des.deskribapenArabera)
        server.register_function(des.sct2term)
        server.register_function(des.sct2desc)
        server.register_function(des.sct2hierarkiak)
        server.register_function(des.desc2sct)
        server.register_function(des.kontzeptuakJaso)
        server.register_function(des.kontzeptuaJaso)
        server.register_function(des.dId2desc)

        print('Serving on http://%s:%s' % (options.host, options.port))
        # server.serve()
        server.serve_forever()
    except KeyboardInterrupt:
        print(sys.stderr, "Bye.")
        exit()



if __name__ == '__main__':
    main()
