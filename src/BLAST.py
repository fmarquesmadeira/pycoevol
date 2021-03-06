﻿###############################################################################
# Encoding utf-8                                                              #
# F. Madeira and L. Krippahl, 2012                                            #
# This code is part of Pycoevol distribution.                                 #
# This work is public domain.                                                 #
###############################################################################

from Parameters import LoadParameters as LP
from os import remove
from shutil import move
from Bio import SeqIO, Entrez
from Bio.Alphabet import IUPAC
from Bio.Blast import NCBIXML, NCBIWWW
from Bio.Blast.Applications import NcbipsiblastCommandline
Entrez.email = "entrez@mail.com"

class psiblast:
    """
    Main code for psiblast search over internet or at local database.
    
    Method for searching homologous sequences:
    PSI-Blast - Altschul et al, 1997
    """
    def __init__(self, id1, id2, psiblast, parameterfile, dirname):
        self.id1 = id1
        self.id2 = id2
        self.psiblast = psiblast
        self.parameterfile = parameterfile
        self.dirname = dirname
        
    def __call__(self, id1, id2, psiblast, parameterfile, dirname):
        self.id1 = id1
        self.id2 = id2
        self.psiblast = psiblast
        self.parameterfile = parameterfile
        self.dirname = dirname

    def searchPSIBLAST(self, id, psiblast):
        "Psi-Blast over a local database or over the internet"
        
        if psiblast == "local":
            threads = LP(self.parameterfile, "psiblast_threading")
            evalue = LP(self.parameterfile, "psiblast_evalue")
            reference_protein = "refseq_protein"
        
            in_sequence = self.dirname + id + ".fa"
            
            output = self.dirname + id + ".xml"
            if threads == False:
                psiblast = NcbipsiblastCommandline(query=in_sequence,
										 db=reference_protein,
										 outfmt=5,
										 threshold=evalue,
										 out=output) 
                psiblast()
            else:
                try:
                    threads = int(threads)
                    psiblast = NcbipsiblastCommandline(query=in_sequence,
                                         db=reference_protein,
                                         outfmt=5,
                                         threshold=evalue,
                                         out=output,
                                         num_threads=threads) 
                    psiblast()
                except: 
                    psiblast = NcbipsiblastCommandline(query=in_sequence,
                                         db=reference_protein,
                                         outfmt=5,
                                         threshold=evalue,
                                         out=output) 
                    psiblast()
            
            try:
                open(self.dirname + id + ".fasta")
                open.close()
                remove(self.dirname + id + ".fa")
            except: 
                move(self.dirname + id + ".fa", self.dirname + id + ".fasta")
        else:
            evalue = LP(self.parameterfile, "psiblast_evalue")
            reference_protein = "refseq_protein"
            
            in_sequence = self.dirname + id + ".fa"
                
            for seq_record in SeqIO.parse(in_sequence,
                                          "fasta", IUPAC.protein):
                sequence = seq_record.seq
        
                psiblast = NCBIWWW.qblast("blastp",
								    reference_protein,
								    sequence,
								    service="psi",
								    expect=evalue,
								    hitlist_size=500)
                psiblast
                
            try:
                open(self.dirname + id + ".fasta")
                open.close()
                remove(self.dirname + id + ".fa")
            except: 
                move(self.dirname + id + ".fa", self.dirname + id + ".fasta")

            output = self.dirname + id + ".xml"
            saveblast = open(output, "w")
            saveblast.write(psiblast.read())
            saveblast.close()
            psiblast.close()

    def validXML(self, id):
        "Checks if the input file is a valid XML"
        
        try:
            input = self.dirname + id + ".xml"
            input_xml = open(input, "r")
            xml = input_xml.readline()
            input_xml.close()
            if xml[0:5] == "<?xml":
                pass
            else:                             
                raise StandardError, "%s - Invalid xml" % (input)
        except:
            raise StandardError, "%s - Invalid xml or not found" % (input)

    def sequencesXML(self, id, psiblast):
        "Extracts records from xml and writes FASTA (full-length) sequences"
        
        thresh_identity = LP(self.parameterfile, "psiblast_identity")
        thresh_coverage = LP(self.parameterfile, "psiblast_coverage")
        
        input = self.dirname + id + ".xml"
        input_xml = open(input, "r")
        
        hits = []
        for record in NCBIXML.parse(input_xml):            
            for align in record.alignments:
                hit_id = align.hit_id
                for hsp in align.hsps:    
                    positives = int(hsp.positives)
                    identities = int(hsp.identities)
                    q_start = int(hsp.query_start)
                    q_end = int(hsp.query_end)
                    query = (q_end - q_start) * 1.0
                    sbjct1 = positives * 1.0
                    coverage = sbjct1 / query * 100
                    sbjct2 = identities * 1.0
                    identity = sbjct2 / query * 100
                    if coverage > thresh_coverage and identity > thresh_identity:
                        hits.append(hit_id)
        input_xml.close()
        
        if hits == []:
            raise StandardError, "%s - No Hits found in PSI-BLAST search" % (input) 
                 
        for hit_id in hits:
            gi = hit_id[hit_id.find("id|") + 4:hit_id.find("|ref")]
            try:
                efetch = Entrez.efetch(db="protein", id=gi, rettype="fasta")
            except:
                try:
                    efetch = Entrez.efetch(db="protein", id=gi, rettype="fasta")
                except:
                    efetch = Entrez.efetch(db="protein", id=gi, rettype="fasta")
                efetch = Entrez.efetch(db="protein", id=gi, rettype="fasta")
            for values in efetch:
                description = values
                break
            sequence = ""
            for values in efetch:
                sequence += values.rstrip("\n")
            try: 
                organism = description[description.find("[") + 1:description.find("]")]
                organism = organism.split()
                if len(organism) != 1:
                    species = str(organism[0] + "_" + organism[1])
                else:
                    species = str(organism[0] + "_" + "sp.")
                output = self.dirname + id + ".blast"
                blast = open(output, "a")
                blast.write("\n" + ">" + species + "\n" + sequence + "\n")
                blast.close()
            except: 
                raise StandardError, "%s - No Hits found in PSI-BLAST search" % (input)    
            
 
        

