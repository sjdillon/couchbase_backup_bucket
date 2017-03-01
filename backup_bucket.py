#==========================================================#
# backup_bucket.py
# sjdillon
# backup coucbhase, zip and delete older backups
#==========================================================#
import os
import datetime
import shutil
import timeit
import smtplib
import socket
import ConfigParser
import traceback

base_dir='/opt/couchbase/backups/'
dump_dir='%s%s/' % (base_dir, 'dump')
archive_dir='%s%s/' % (base_dir, 'archive')
config_file='cb.cfg'

def get_config(section, key):
        config = ConfigParser.ConfigParser()
        config.readfp(open(base_dir+config_file))
        val=config.get(section, key)
        return val

def get_credentials():
        uname=get_config('credentials', 'uname')
        pw=get_config('credentials', 'pw')
        return uname, pw

def send_email(msg):
	domain=get_config('email','domain')
        from_addr='%s@%s' % (socket.gethostname().split('.')[0],domain)
        to_addr=get_config('backups','alert_email')
        subject='couchbase backup bucket failed'
        body=msg
        message = """Subject: %s\n\n%s\n""" % (subject, body)

        server = smtplib.SMTP('localhost')
        server.sendmail(from_addr,to_addr,message)
        server.quit()
        print 'send email'

def rotate(del_dir):
        ''' delete oldest zips, keep only X copies '''
        keep=get_config('backups','retention_count')
        sorted_files=sorted(os.listdir(del_dir))
        delete = len(sorted_files) - int(keep)
        for f in range(0,delete):
                print "Deleting: " + sorted_files[f]
                os.remove(del_dir+'/'+ sorted_files[f] )

def zipit(bucket,indir, destdir):
        ''' zip a folder to new location '''
        zip_name='%s_%s' % (bucket,datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S"))
        command ='zip -r %s/%s.zip %s*' % (destdir, zip_name, indir)
        out=os.system(command)
        return out

def delete_folder(indir):
        ''' remove folder and subfolders '''
        shutil.rmtree(indir)

def run_backup(bucket):
        uname,pw=get_credentials()
        command="/opt/couchbase/bin/cbbackup http://127.0.0.1:8091 %s -u %s -p '%s' -b %s" % (dump_dir, uname, pw, bucket)
        status=os.system(command)
        return status

def run_all(bucket,archive_dir):
        try:
                archive_dir = archive_dir + bucket
                if not os.path.exists(archive_dir):
                        os.makedirs(archive_dir)
                ## backup couchbase bucket
                start = timeit.default_timer()
                print '###start backup'
                status=run_backup(bucket)
                print '###execution time:%fs' % (timeit.default_timer()-start)
                if status!=0:
                        raise NameError('couchbase backup failed')

                ## zip backup and move to archive dir
                start = timeit.default_timer()
                print '###zip backup'
                zipit(bucket,dump_dir,archive_dir)
                print '###execution time:%fs' % (timeit.default_timer()-start)

                ## keep only 6 backups
                start = timeit.default_timer()
                print '###delete old backups'
                rotate(archive_dir)
                print '###execution time:%fs' % (timeit.default_timer()-start)

                ## clear dumps dir - must be empty for cbbackup command to work
                start = timeit.default_timer()
                print '###purge dump folder'
                delete_folder(dump_dir)
                print '###execution time:%fs' % (timeit.default_timer()-start)
        except Exception, e:
                print 'ERROR: %s'% ( str(e) )
                traceback.print_exc()
                send_email(str(e))



buckets=get_config('backups','bucket_names')
for bucket in buckets.split():
        run_all(bucket,archive_dir)
