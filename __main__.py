import argparse
import datetime
import re

from .beans import Manager
m = Manager()


# User Options
def options(*args, **kwds):
    '''
    User options.

    @return: {Namespace}
    '''
    parser = argparse.ArgumentParser(prog            = 'librarian',
                                     formatter_class = argparse.ArgumentDefaultsHelpFormatter,
                                     description     = 'A library building helper')

    parser.add_argument('-e', '--experiment',   dest     = "experiment",
                        action  = "store",      required = True,
                        help    = "Experiment name")

    parser.add_argument('-c', '--config',       dest     = "configfile",
                        action  = "store",      required = False,
                        help    = "Add a configuration file " +
                                  "for external software")
    parser.add_argument('-d', '--date',         dest     = "date",
                        action  = "store",      required = False,
                        default = datetime.date.today(),
                        help    = "Date of the experiment, as YYY-MM-DD")

    options = parser.parse_args()

    m.set_verbose()

    return options


if __name__ == "__main__":

    options = options()

    m.info('Creating project: {0}'.format(options.experiment))

    if isinstance(options.date, datetime.date):
        m.experiment_date = options.date
    else:
        date_regex = re.compile('(\d{4})\-(\d{2})\-(\d{2})')
        d = date_regex.search(options.date)
        if not d:
            m.exception('Experiment date wrongly formated')
        m.set_experiment_date(d[1], d[2], d[3])

    m.experiment_name = options.experiment
    m.set_experiment_configuration_file(options.configfile)
    m.init_experiment()
