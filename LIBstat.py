import sys, math, numpy;

numpy.set_printoptions(linewidth=162,precision=7,suppress=True)#,formatter={'float': '{:2.2f}'.format})

buckets  = [[ 1, 1],[ 2, 2],[ 3, 3],[ 4, 4],[ 5, 5],[ 6, 6],[ 7, 7],[ 8, 8],
            [ 9, 9],[10,11],[12,13],[14,15],[16,17],[18,19],[20,21],
            [22,23],[24,25],[26,28],[29,31],[32,35],[36,41],[42,52],[53,610]]
bbound   = len(buckets)
bindices = range(0,bbound)
dbound   = 20
dindices = range(0,dbound)

def bucket(length):
    bu   = -1
    for bi in bindices:
        if length >= buckets[bi][0] and length <= buckets[bi][1]:
            return bi
    print("(sentence length {} out of range)".format(length), file=sys.stderr)
    sys.stderr.close()
    exit(1)

class Stat:
    def __init__(self):
        self.dmax   = 0
        self.total  = 0
        self.flushed= False
        self.dcnt   = [0]  * dbound
        self.bcnt   = [0]  * bbound
        self.bmed   = [0]  * bbound
        self.blen   = [[]] * bbound
        self.blmax  = [0]  * bbound
        self.joint  = numpy.reshape( numpy.array([0.0] * bbound * dbound ), (bbound, dbound) )
        self.cond   = numpy.reshape( numpy.array([0.0] * bbound * dbound ), (bbound, dbound) )
        self.bdcnt  = numpy.reshape( numpy.array([ 0 ] * bbound * dbound ), (bbound, dbound) )
        
    def add(self,depth,length):
        assert depth < dbound
        self.total = self.total + 1                       # total number of sentences
        self.dmax  = max([depth,self.dmax])               # maximum depth
        self.dcnt[depth] = self.dcnt[depth] + 1           # total sentences per depth
        bi = bucket(length)
        self.bcnt[bi] = self.bcnt[bi] + 1                 # total sentences in bucket
        self.blen[bi] = self.blen[bi] + [length]          # all sentence lengths in bucket
        self.blmax[bi] = max([length,self.blmax[bi]])     # max sentence length in bucket        
        self.bdcnt[bi][depth] = self.bdcnt[bi][depth] + 1 # total sentences per bucket and depth

    def compute_types(self):
        for bi in bindices:
            if self.blen[bi] != []:
                halfway = int(len(self.blen[bi])/2)
#                if halfway + halfway < len(self.blen[bi]):
#                    self.bmed[bi] = int((self.blen[bi][halfway] + self.blen[bi][halfway+1])/2) # est. median
#                else:
                self.bmed[bi] = self.blen[bi][halfway]                                     # median
                self.blen[bi] = list(set(self.blen[bi]))                                   # unique types
                
    def assertions(self):
        dcnts = 0
        for di in dindices:
            dcnts  = dcnts  + self.dcnt[di]
            bdcnts = 0
            for bi in bindices:
                bdcnts = bdcnts + self.bdcnt[bi][di]  
            assert bdcnts == self.dcnt[di]
        assert self.total == dcnts
        bcnts = 0
        for bi in bindices:
            bdcnts = 0
            for di in dindices:
                bdcnts = bdcnts + self.bdcnt[bi][di]  
            assert bdcnts == self.bcnt[bi]
            bcnts  = bcnts + self.bcnt[bi]
        assert self.total == bcnts
        for bi in bindices:
            if self.bcnt[bi]:
                assert len(self.blen[bi]) == self.bcnt[bi]
                assert self.blen[bi][-1] == self.blmax[bi]

    def print_depth_coverage(self):
        assert self.flushed
        depth_title     = []
        depth_dcnt      = []
        depth_cum_perc  = []
        depth_perc      = []
        cumperc = 0.0
        cum     = 0
        for i in dindices:
            if self.dcnt[i] >= 0:
                cumperc = cumperc + self.dcnt[i]/self.total
                cum     = cum     + self.dcnt[i]
                depth_title.append(" {:7} ".format(i))
                depth_dcnt.append(" {:7} ".format(self.dcnt[i]))
                depth_perc.append("+{:7.3f}\\% ({})".format(self.dcnt[i]/self.total*100,self.dcnt[i]))
                depth_cum_perc.append("{:7.2f}\\%".format(cumperc*100))
        print(" &",self.total,"&"," & ".join(depth_cum_perc[0:6]+depth_perc[6:self.dmax+1]),"\\\\")
#        print("stat               depths=","\t".join(depth_title))
#        print("stat         depth counts=","\t".join(depth_dcnt))
#        print("stat     depth percentage= "," & ".join(depth_perc))
#        print("stat depth cum percentage= "," & ".join(depth_cum_perc))
#        print("stat                total=",self.total)

    def print_length_distribution(self):
        assert self.flushed
        total_prob = 0.0
        for bi in bindices:
            if self.bcnt[bi] > 0:
                total_prob = total_prob + self.bcnt[bi] / self.total 
#                print("prob len bucket={}\tmedian len={}\tP(length)={:7.2%}\tP(<=length)={:7.2%}".
#                      format(bi, self.bmed[bi], self.bcnt[bi] / len(self.blen[bi]) / self.total, total_prob ))
                print("{:7.1f}  {}".format(self.bmed[bi] * .25, self.bcnt[bi] / len(self.blen[bi]) / self.total * 1000.0 ))

    def print_joint_distribution(self):
        joint_total_count = 0
        joint_total = 0.0
        for bi in bindices:
            for di in dindices:
                if self.bdcnt[bi][di] > 0:
                    joint_total_count = joint_total_count +  self.bdcnt[bi][di] 
                    joint_total = joint_total + self.bdcnt[bi][di] / self.total
                    self.joint[bi][di] = self.bdcnt[bi][di] / len(self.blen[bi]) / self.total
#                    self.joint[bi][di] = self.bdcnt[bi][di] / self.total
                    self.cond[bi][di] = self.bdcnt[bi][di] / self.bcnt[bi]
#                    print("joint {} b:{:2} median:{:2} lens:{:2}".format(di, bi, self.bmed[bi], len(self.blen[bi])), 
#                          "P(length)={:7.2%}".format(    self.bcnt[bi]      / len(self.blen[bi]) / self.total),
#                          "P(d={},l)={:7.2%}".format(di, self.bdcnt[bi][di] / len(self.blen[bi]) / self.total), # joint prob
#                          "P(d={}|b={})={:7.2%}".format(di, bi, self.bdcnt[bi][di] / self.bcnt[bi] ),           # cond  prob
#                          "P(d={},b)={:7.2%}".format(di, self.bdcnt[bi][di]                      / self.total),
#                          "jtotal={:7.2%}"   .format(joint_total))
                    if joint_total_count == self.total:
                        break
        print("# cond dindices[6:]:")
        for bi in bindices:
            cond = 0.0
            for di in dindices[6:]:
                cond = cond + self.cond[bi][di]
            print("{:7.1f}  {}  # {:10.9f}".format(self.bmed[bi] * .25, cond * 100.0 * 20, cond ))
        print("# cond dindices[5:]:")
        for bi in bindices:
            cond = 0.0
            for di in dindices[5:]:
                cond = cond + self.cond[bi][di]
            print("{:7.1f}  {}  # {:10.9f}".format(self.bmed[bi] * .25, cond * 100.0 * 4, cond ))
        print("# cond dindices[4:]:")
        for bi in bindices:
            cond = 0.0
            for di in dindices[4:]:
                cond = cond + self.cond[bi][di]
            print("{:7.1f}  {}  # {:10.9f}".format(self.bmed[bi]* .25, cond * 100.0 * 0.8, cond ))
        print("# cond dindices[3:]:")
        for bi in bindices:
            cond = 0.0
            for di in dindices[3:]:
                cond = cond + self.cond[bi][di]
            print("{:7.1f}  {}  # {:10.9f}".format(self.bmed[bi]* .25, cond * 100.0 * .4, cond ))
        print("# cond dindices[2:]:")
        for bi in bindices:
            cond = 0.0
            for di in dindices[2:]:
                cond = cond + self.cond[bi][di]
            print("{:7.1f}  {}  # {:10.9f}".format(self.bmed[bi]* .25, cond * 100.0 * .4, cond ))
        print("# cond dindices[1:]:")
        for bi in bindices:
            cond = 0.0
            for di in dindices[1:]:
                cond = cond + self.cond[bi][di]
            print("{:7.1f}  {}  # {:10.9f}".format(self.bmed[bi]* .25, cond * 100.0 * .4, cond ))
        print("# cond dindices[0:]:")
        for bi in bindices:
            cond = 0.0
            for di in dindices[0:]:
                cond = cond + self.cond[bi][di]
            print("{:7.1f}  {}  # {:10.9f}".format(self.bmed[bi]* .25, cond * 100.0 * .4, cond ))

            
        print("# joint dindices[6:]:")    
        for bi in bindices:
            joint = 0.0
            for di in dindices[6:]:
                joint = joint + self.joint[bi][di]
            print("{:7.1f}  {}  # {:10.9f}".format(self.bmed[bi], joint * 10000.0, joint ))
        print("# joint dindices[5:]:")                        
        for bi in bindices:
            joint = 0.0
            for di in dindices[5:]:
                joint = joint + self.joint[bi][di]
            print("{:7.1f}  {}  # {:10.9f}".format(self.bmed[bi], joint * 10000.0, joint ))
        print("# joint dindices[4:]:")                        
        for bi in bindices:
            joint = 0.0
            for di in dindices[4:]:
                joint = joint + self.joint[bi][di]
            print("{:7.1f}  {}  # {:10.9f}".format(self.bmed[bi], joint * 10000.0, joint ))
        print("# joint dindices[3:]:")                      
        for bi in bindices:
            joint = 0.0
            for di in dindices[3:]:
                joint = joint + self.joint[bi][di]
            print("{:7.1f}  {}  # {:10.9f}".format(self.bmed[bi], joint * 10000.0, joint ))
        print("# joint dindices[2:]:")                      
        for bi in bindices:
            joint = 0.0
            for di in dindices[2:]:
                joint = joint + self.joint[bi][di]
            print("{:7.1f}  {}  # {:10.9f}".format(self.bmed[bi], joint * 10000.0, joint ))
        print("# joint dindices[1:]:")                      
        for bi in bindices:
            joint = 0.0
            for di in dindices[1:]:
                joint = joint + self.joint[bi][di]
            print("{:7.1f}  {}  # {:10.9f}".format(self.bmed[bi], joint * 10000.0, joint ))
        print("# joint dindices[0:]:")                      
        for bi in bindices:
            joint = 0.0
            for di in dindices[0:]:
                joint = joint + self.joint[bi][di]
            print("{:7.1f}  {}  # {:10.9f}".format(self.bmed[bi], joint * 10000.0, joint ))
                    
    def flush(self):
        for bi in bindices:
            self.blen[bi].sort()
        self.assertions()
        self.compute_types()
        self.flushed = True
        # print_depth_coverage(self)
        # self.print_length_distribution()
        # self.print_joint_distribution()

        for di in dindices[0:]:
            if self.dcnt[di]:
                cum = 0.0
                print("# cond depth {}:".format(di))                      
                for bi in bindices:
                    cum = cum + self.bdcnt[bi][di] / self.dcnt[di]
                    print("{:7.1f}  {}  # {:10.9f}".format(self.bmed[bi], cum * 40.0, cum ))
        
        return        

    
