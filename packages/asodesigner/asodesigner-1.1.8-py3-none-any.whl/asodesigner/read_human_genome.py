import bisect
from pathlib import Path

import gffutils

from .consts import HUMAN_GTF, HUMAN_DB_BASIC_INTRONS, HUMAN_DB_BASIC_INTRONS_GZ
from .genome_file_utils import read_human_genome_fasta_dict
from .LocusInfo import LocusInfo
from .timer import Timer

from tqdm import tqdm
import threading
import time



def cond_print(text, verbose=False):
    if verbose:
        print(text)



def create_human_genome_db(path: Path, create_introns=False):
    print("Creating human genome database. WARNING - this is slow!")
    total_bytes = HUMAN_GTF.stat().st_size if HUMAN_GTF.is_file() else None
    stop_event = threading.Event()

    def _monitor():
        bar_kwargs = {
            "desc": "Building genome DB",
            "unit": "B",
            "unit_scale": True,
            "unit_divisor": 1024,
        }
        if total_bytes:
            bar_kwargs["total"] = total_bytes
        else:
            bar_kwargs["total"] = None

        last_size = 0
        with tqdm(**bar_kwargs) as bar:
            while not stop_event.is_set():
                if path.exists():
                    size = path.stat().st_size
                    if bar.total is not None and size > bar.total:
                        bar.total = size
                    increment = max(0, size - last_size)
                    if increment:
                        bar.update(increment)
                        last_size = size
                time.sleep(0.5)

            if path.exists():
                size = path.stat().st_size
                if bar.total is not None and size > bar.total:
                    bar.total = size
                increment = max(0, size - last_size)
                if increment:
                    bar.update(increment)

    monitor = threading.Thread(target=_monitor, daemon=True)
    monitor.start()

    try:
        with Timer() as t:
            db = gffutils.create_db(str(HUMAN_GTF), dbfn=str(path), force=True, keep_order=True,
                                    merge_strategy='merge', sort_attribute_values=True)
            if create_introns:
                db.update(list(db.create_introns()))
    finally:
        stop_event.set()
        monitor.join()

    print(f"DB create took: {t.elapsed_time}s")
    return db


def get_human_genome_annotation_db(create_db=False, verbose=False):
    db_path = HUMAN_DB_BASIC_INTRONS

    with Timer() as t:
        if not db_path.is_file():
            if HUMAN_DB_BASIC_INTRONS_GZ.is_file():
                raise ValueError(
                    f"DB file is not unzipped: {HUMAN_DB_BASIC_INTRONS_GZ}, please unzip to use! (Consider README.md)")

            if create_db:
                db = create_human_genome_db(db_path, create_introns=True)
            else:
                raise ValueError(
                    f"DB not found in path: {str(db_path)}, either download it or create (please consider README.md)")
        else:
            db = gffutils.FeatureDB(str(db_path))
    # TODO: use verbose
    # if verbose:
    print(f"Time took to read human annotations: {t.elapsed_time}")

    return db


def get_locus_to_data_dict(create_db=False, include_introns=False, gene_subset=None):
    db = get_human_genome_annotation_db(create_db)
    fasta_dict = read_human_genome_fasta_dict()

    locus_to_data = dict()
    locus_to_strand = dict()

    basic_features = ['exon', 'gene', 'stop_codon', 'UTR']

    feature_types = basic_features.copy()
    if include_introns:
        feature_types.append('intron')

    for feature in db.features_of_type(feature_types, order_by='start'):
        chrom = feature.seqid
        if 'chrM' == chrom:
            continue
        locus_tags = feature.attributes['gene_name']
        if len(locus_tags) != 1:
            raise ValueError(f"Multiple loci: {locus_tags}")
        locus_tag = locus_tags[0]

        if gene_subset is not None:
            if locus_tag not in gene_subset:
                continue

        if locus_tag not in locus_to_data:
            locus_info = LocusInfo()
            locus_to_data[locus_tag] = locus_info
        else:
            locus_info = locus_to_data[locus_tag]

        if feature.featuretype == 'exon':
            exon = feature
            seq = fasta_dict[chrom].seq[exon.start - 1: exon.end]
            if exon.strand == '-':
                seq = seq.reverse_complement()
            seq = seq.upper()

            bisect.insort(locus_info.exons, (exon.start - 1, seq))
            bisect.insort(locus_info.exon_indices, (exon.start - 1, exon.end))
            locus_to_strand[locus_tag] = exon.strand

        elif feature.featuretype == 'intron' and include_introns:
            intron = feature
            seq = fasta_dict[chrom].seq[intron.start - 1: intron.end]

            if intron.strand == '-':
                seq = seq.reverse_complement()
            seq = seq.upper()

            bisect.insort(locus_info.introns, (intron.start - 1, seq))
            bisect.insort(locus_info.intron_indices, (intron.start - 1, intron.end))
            locus_to_strand[locus_tag] = intron.strand

        elif feature.featuretype == 'gene':
            gene = feature
            seq = fasta_dict[chrom].seq[gene.start - 1: gene.end]

            if gene.strand == '-':
                seq = seq.reverse_complement()
            seq = seq.upper()

            locus_info.strand = gene.strand
            locus_info.cds_start = gene.start - 1
            locus_info.cds_end = gene.end
            locus_info.full_mrna = seq
            locus_to_strand[locus_tag] = gene.strand


        elif 'UTR' in feature.featuretype:
            utr = feature
            bisect.insort(locus_info.utr_indices, (utr.start - 1, utr.end))
        elif feature.featuretype == 'stop_codon':
            locus_info.stop_codons.append((feature.start, feature.end))
        else:
            print("Feature type: ", feature.featuretype)

        locus_info = locus_to_data[locus_tag]
        gene_type = feature.attributes['gene_type']
        locus_info.gene_type = gene_type


    for locus_tag in locus_to_data:
        locus_info = locus_to_data[locus_tag]
        if locus_to_strand[locus_tag] == '-':
            locus_info.exons.reverse()
            if include_introns:
                locus_info.introns.reverse()
        locus_info.exons = [element for _, element in locus_info.exons]

        if include_introns:
            locus_info.introns = [element for _, element in locus_info.introns]

    return locus_to_data
