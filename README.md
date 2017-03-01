# couchbase_backup_bucket
python script to backup coucbhase, zip and delete older backups

# Purpose
Detail the process for creating a cron job to backup Couchbase buckets

# Details
The backup script will:
1. backup one or more buckets
2. zip backup files
3. maintain configurable amount of historical backup copies
 
The deploy playbook will:
1. create a backup directory structure on couchbase nodes
2. push the backup_buckets script and configuration file
3. schedules a cron jo
