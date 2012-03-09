import logging
log = logging.getLogger("analysis_method")

import os
import scheme
import algorithm
import submodels
from analysis import Analysis, AnalysisError

class UserAnalysis(Analysis):

    def do_analysis(self):
        """Process everything when search=user"""
        models = self.cfg.models

        current_schemes = [s for s in self.cfg.schemes]
        self.total_scheme_num = len(current_schemes)
        if self.total_scheme_num>0:
            for s in current_schemes:
                 self.analyse_scheme(s, models)
            self.write_best_scheme(current_schemes)
        else:
            log.error("Search set to 'user', but no user schemes detected in .cfg file. Please check.")
            raise PartitionFinderError

class GreedyAnalysis(Analysis):

    def do_analysis(self):
        '''A greedy algorithm for heuristic partitioning searches'''
        log.info("Performing greedy analysis")
        models = self.cfg.models
        model_selection = self.cfg.model_selection
        partnum = len(self.cfg.partitions)

        self.total_scheme_num = submodels.count_greedy_schemes(partnum)
        log.info("This will result in a maximum of %s schemes being created", self.total_scheme_num)

        self.total_subset_num = submodels.count_greedy_subsets(partnum)
        log.info("PartitionFinder will have to analyse a maximum of %d subsets of sites to complete this analysis" %(self.total_subset_num))

        if self.total_subset_num>10000:
            log.warning("%d is a lot of subsets, this might take a long time to analyse", self.total_subset_num)
            log.warning("Perhaps consider using a different search scheme instead (see Manual)")

        #clear any schemes that are currently loaded
        # TODO Not sure we need this...
        self.cfg.schemes.clear_schemes()        
                
        #start with the most partitioned scheme
        start_description = range(len(self.cfg.partitions))
        start_scheme = scheme.create_scheme(self.cfg, 1, start_description)
        log.info("Analysing starting scheme (scheme %s)" % start_scheme.name)
        self.analyse_scheme(start_scheme, models)
        
        def get_score(my_scheme):
            #TODO: this is bad. Should use self.cfg.model_selection, or write
            #a new model_selection for scheme.py
            if model_selection=="aic":
                score=my_scheme.aic
            elif model_selection=="aicc":
                score=my_scheme.aicc
            elif model_selection=="bic":
                score=my_scheme.bic
            else:
                log.error("Unrecognised model_selection variable '%s', please check" %(score))
                raise AnalysisError
            return score

        best_scheme = start_scheme
        best_score  = get_score(start_scheme)
                         
        step = 1
        cur_s = 2

        #now we try out all lumpings of the current scheme, to see if we can find a better one
        #and if we do, we just keep going
        while True:
            log.info("***Greedy algorithm step %d***" % step)

            #get a list of all possible lumpings of the best_scheme
            lumpings = algorithm.lumpings(start_description)

            #we reset the counters as we go, for better user information
            self.total_scheme_num = len(lumpings)
            self.schemes_analysed = 0

            best_lumping_score = None
            for lumped_description in lumpings:
                lumped_scheme = scheme.create_scheme(self.cfg, cur_s, lumped_description)
                cur_s = cur_s + 1
                self.analyse_scheme(lumped_scheme, models)
                new_score = get_score(lumped_scheme)

                if best_lumping_score==None or new_score<best_lumping_score:
                    best_lumping_score  = new_score
                    best_lumping_scheme = lumped_scheme
                    best_lumping_desc   = lumped_description

            if best_lumping_score<best_score:
                best_scheme = best_lumping_scheme
                best_score  = best_lumping_score
                start_description = best_lumping_desc               
                if len(set(best_lumping_desc))==1: #then it's the scheme with everything equal, so quit
                    break
                step = step+1

            else:
                break

        log.info("Greedy algorithm finished after %d steps" % step)
        log.info("Highest scoring scheme is scheme %s, with %s score of %.3f"
                 %(best_scheme.name, model_selection, best_score))

        best_schemes_file = os.path.join(self.cfg.output_path, 'best_schemes.txt')
        best_scheme.write_summary(
            best_schemes_file, 'wb', 
            "Best scheme according to Greedy algorithm, analysed with %s\n\n" % model_selection)
        log.info("Information on best scheme is here: %s" %(best_schemes_file))

        current_schemes = [s for s in self.cfg.schemes]
        current_schemes.sort(key=lambda s: int(s.name), reverse=False)

        self.write_all_schemes(current_schemes) #this also writes a file which has info on all analysed schemes, useful for extra analysis if that's what you're interested in...

class AllAnalysis(Analysis):

    def do_analysis(self):
        models = self.cfg.models
        partnum = len(self.cfg.partitions)

        self.total_scheme_num = submodels.count_all_schemes(partnum)
        log.info("Analysing all possible schemes for %d starting partitions", partnum)
        log.info("This will result in %s schemes being created", self.total_scheme_num)
        self.total_subset_num = submodels.count_all_subsets(partnum)
        log.info("PartitionFinder will have to analyse %d subsets to complete this analysis" %(self.total_subset_num))
        if self.total_subset_num>10000:
            log.warning("%d is a lot of subsets, this might take a long time to analyse", self.total_subset_num)
            log.warning("Perhaps consider using a different search scheme instead (see Manual)")

        #clear any schemes that are currently loaded
        self.cfg.schemes.clear_schemes()

        #iterate over submodels, which we can turn into schemes afterwards in the loop
        model_iterator = submodels.submodel_iterator([], 1, partnum)

        scheme_name = 1
        list_of_schemes = []
        for m in model_iterator:
            s = scheme.model_to_scheme(m, scheme_name, self.cfg)
            scheme_name = scheme_name+1
            self.analyse_scheme(s, models)
            list_of_schemes.append(s)
        self.write_best_scheme(list_of_schemes)

def choose_method(search):
    if search == 'all':
        method = AllAnalysis
    elif search == 'user':
        method = UserAnalysis
    elif search == 'greedy':
        method = GreedyAnalysis
    else:
        log.error("Search algorithm '%s' is not yet implemented", search)
        raise AnalysisError
    return method

