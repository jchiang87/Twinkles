import numpy as np
import sqlite3 as db2_imp

def nullFunc(*args):
    return None

class Database(object):
    def __init__(self, dbfile):
        self.dbfile = dbfile
    def apply(self, sql, args=None, cursorFunc=nullFunc):
        sql = sql.replace('?', '%s')
        my_connection = db2_imp.connect(self.dbfile)
        cursor = my_connection.cursor()
        try:
            if args is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, args)
            results = cursorFunc(cursor)
        except db2_imp.DatabaseError, message:
            cursor.close()
            my_connection.close()
            raise db2_imp.DatabaseError, message
        cursor.close()
        if cursorFunc is nullFunc:
            my_connection.commit()
        my_connection.close()
        return results


def count_visits(db, thresh=8000):
    sql = 'select fieldID from Summary'
    fieldIDs = db.apply(sql, cursorFunc=lambda curs : [x[0] for x in curs])

    count = {}
    for fieldID in fieldIDs:
        if not count.has_key(fieldID):
            count[fieldID] = 0
        count[fieldID] += 1
    ddfs = []

    for key, value in count.items():
        if value > thresh:
            ddfs.append(key)
            sql = 'select fieldRA, fieldDec from Field where fieldID=%i' % key
            ra, decl = db.apply(sql, cursorFunc=lambda curs : [x for x in curs][0])
            print key, ra, decl

class Visits(object):
    sql_tpl = "select expMJD from Summary where fieldId=%i and filter='%s' order by expMJD asc"
    def __init__(self, fieldId):
        self.fieldId = fieldId
    def get_mjds(self, filter_):
        if filter_ not in 'ugrizy':
            raise RuntimeError("Invalid filter selection:", filter_)
        sql = self.sql_tpl % (self.fieldId, filter_)
        mjds = db.apply(sql, cursorFunc=lambda curs : [x[0] for x in curs])
        return mjds

#ddfs = (290, 744, 1427, 2412, 2786)
#for item in ddfs:
#    sql = 'select fieldRA, fieldDec from Field where fieldID=%i' % item
#    ra, decl = db.apply(sql, cursorFunc=lambda curs : [entry for entry in curs][0])
#    print item, ra, decl

if __name__ == '__main__':
    import pylab_plotter as plot
    plot.pylab.ion()
#    db = Database('enigma_1189_sqlite.db')
    db = Database('kraken_1042_sqlite.db')
    fieldId = 1427

    colors = 'krgbycm'

    mjd0 = 59580
    five_month_intervals = mjd0 + np.arange(30)*150.

    visits = Visits(fieldId)
    mjds = {}
    bands = 'ugrizy'
    for i, band in enumerate(bands):
        mjds[band] = visits.get_mjds(band)
        #
        # plot cumulative number of visits vs MJD
        #
        if i == 0:
            win0 = plot.xyplot(mjds[band], range(len(mjds[band])),
                               xname='MJD', yname='# of visits',
                               color=colors[i])
        else:
            plot.xyplot(mjds[band], range(len(mjds[band])), oplot=1,
                        color=colors[i])
    for mjd in five_month_intervals:
        plot.vline(mjd)
    win0.set_title('all visits, kraken_1042, fieldID=1427')
    plot.legend(colors[:len(bands)], bands)
    plot.save('all_visits_kraken_1042_fieldID_1427.png')
    for i, band in enumerate('ugrizy'):
        #
        # Limit to one visit per night
        #
        captured = {}
        my_visits = []
        for mjd in mjds[band]:
            if int(mjd) not in captured.keys():
                captured[int(mjd)] = 1
                my_visits.append(mjd)
        if i == 0:
            win1 = plot.xyplot(my_visits, range(len(my_visits)),
                               xname='MJD', yname="# of visits",
                               color=colors[i])
        else:
            plot.xyplot(my_visits, range(len(my_visits)),
                        color=colors[i], oplot=1)
    for mjd in five_month_intervals:
        plot.vline(mjd)
    win1.set_title('one visit per night, kraken_1042, fieldID=1047')
    plot.legend(colors[:len(bands)], bands)
    plot.save('one_visit_per_night_kraken_1042_fieldID_1427.png')
