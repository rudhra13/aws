#!/bin/bash
    ##__AUTHOR: RUDHRA RAI__##

    
        # +---------------------------------------+
        # |  This Script will take backup of all  |
        # |   database and store backup in S3     |
        # |  Bucket in a tar file and remove the  |
        # |  previous backups [of 15 days before] |
        # +---------------------------------------+ 


    BUCKET_NAME="db-dumps"
    PROJECT_NAME="project"
    ## DB's ##
    DB1="Mongo"
    DB2="mysql"
    DB3="redis"

    ## Set Variables ##
    TIMESTAMP=`date +%d-%b-%y`
    OLD_TIMESTAMP=`date +%d-%b-%y --date "15 days ago"`
    flag=0
    # In this function mail is sent on error occurance
    # provide DB name (for which db)
    #         message (what message needs to be sent with mail)
    send_mail(){
        DB=$1
        STATUS=$2
        MESSAGE=$3
    	MAILFR=""
	MAILTO=""
	SMTPPASS="jlemjwlhioxjxomg"
	echo -e "$MESSAGE" | /usr/bin/mailx -v -s "$PROJECT_NAME $DB of date-$TIMESTAMP $STATUS:" -S smtp-use-starttls -S ssl-verify=ignore -S smtp-auth=login -S smtp=smtp://smtp.gmail.com:587 -S from="$MAILFR(DB Backup Script)" -S smtp-auth-user="$MAILFR" -S smtp-auth-password="$SMTPPASS" -S ssl-verify=ignore -S nss-config-dir=/home/centos/.certs $MAILTO
	}

    # In this function dumps are sent to s3
    # provide DB name
    #        backup_dir(where backups is made)
    #        backup name(by which name backup is made)
    send_to_s3(){
        DB=$1
        BACKUP_DIR=$2
        BACKUP_NAME=$3
       
        ##  Transfer Backup to s3 ##
        echo "[$DB]Transferring Backup to s3.." >> db_backup.log
        #aws s3 cp ./testfile s3://yourBucketName/any/path/you/like
        AWS_ACCESS_KEY_ID="ACCESS KEY" AWS_SECRET_ACCESS_KEY="SECRET KEY" /usr/bin/aws s3 cp $BACKUP_DIR/$BACKUP_NAME.tar.gz s3://$BUCKET_NAME/$PROJECT_NAME/$BACKUP_DIR/ --region us-east-2
        STATUS="$?"
        if [ "$STATUS" != "0" ];then
            echo "[$DB]sending mail with $STATUS ERROR" >> db_backup.log
            send_mail $DB "ERROR" "$DB Dump NOT created properly, Process exit with STATUS: $STATUS"
        else
            echo "[$DB]Backup Transferred to s3 [bucket-name: $BUCKET_NAME]" >> db_backup.log
        fi
    }

    # In this function last 15th day backup is removed
    # provides DB name
    #           OLD File Name(to delete the file of before 15 days)
    remove_previous_backup(){
        DB=$1
        BACKUP_DIR=$2
        BACKUP_NAME=$3
        OLD_FILENAME=$4
        cd $BACKUP_DIR
        if [ -f "$OLD_FILENAME.tar.gz" ];then
            rm -rf "$OLD_FILENAME.tar.gz"
            cd ..
            echo "[$DB]old $OLD_FILENAME.tar.gz removed" >> db_backup.log
        else
            cd ..
            echo "[$DB]old $OLD_FILENAME.tar.gz not found" >> db_backup.log
        fi
    
    }

    # In this function size of dump has been checked
    size_check(){
        DB=$1
        BACKUP_DIR=$2
        BACKUP_NAME=$3
        OLD_FILENAME=$4
        LEAST_DUMPSIZE=$5

        cd $BACKUP_DIR
        DUMP_SIZE=`ls -l | grep $BACKUP_NAME.tar.gz | awk '{print $5}'`
        cd ..
        if [ "$DUMP_SIZE" -lt "$LEAST_DUMPSIZE" ];then
            echo "[$DB]ERROR dump not created" >> db_backup.log
            send_mail $DB "ERROR" "$DB Backup doesn't got created properly, as size of tar created in less than $LEASTDUMP_SIZE"
        else
            rm -rf $BACKUP_NAME 
            echo "[$DB]Tar file Created" >> db_backup.log
            echo "[$DB]Filename: $BACKUP_NAME.tar.gz" >> db_backup.log
            send_to_s3 $DB $BACKUP_DIR $BACKUP_NAME
            remove_previous_backup $DB $BACKUP_DIR $BACKUP_NAME $OLD_FILENAME
            STAT="$?"
            if [ "$STAT" == "0" ];then
		flag=$(( $flag + 1 ))
	    fi
        fi
    }

    # In this function file has been compressed
    dump_compression(){
        DB=$1
        BACKUP_NAME=$2
        BACKUP_DIR=$3
        DUMP_NAME=$4
        
        echo "[$DB]Creating tar of dump..." >> db_backup.log
        mkdir -p $BACKUP_DIR
        mv $DUMP_NAME $BACKUP_NAME
        tar -zcvf $BACKUP_DIR/$BACKUP_NAME.tar.gz $BACKUP_NAME
        size_check $DB $BACKUP_DIR $BACKUP_NAME $OLD_FILENAME $LEAST_DUMPSIZE

    }

    # In this function file compression command 
    # status has been checked 
    status_check(){

        DB=$1
        BACKUP_DIR=$2
        BACKUP_NAME=$3
        OLD_FILENAME=$4
        LEAST_DUMPSIZE=$5
        DUMP_NAME=$6
        STATUS=$7

        if [ "$STATUS" != "0" ];then
            echo "[$DB]sendmail function with $STATUS ERROR" >> db_backup.log
            send_mail $DB "ERROR" "$DB Dump NOT created properly, Process exit with STATUS: $STATUS"
        else
            echo "[$DB]Dump Created" >> db_backup.log
            dump_compression $DB $BACKUP_NAME $BACKUP_DIR $DUMP_NAME
        fi
            
    }

    # This function takes backup of mongo database
    mongodb_backup(){

    ###### Set Parameters ######
        DB=$DB1
        COMMAND_PATH="/usr/bin/mongodump"
        BACKUP_DIR="$DB-dumps"
        BACKUP_NAME="$BACKUP_DIR-$TIMESTAMP"
        OLD_FILENAME="$BACKUP_DIR-$OLD_TIMESTAMP"
        LEAST_DUMPSIZE="5"
        DUMP_NAME="dump"

        ## Create Mongo Dump ##
        echo "[$DB]Creating $DB Dump on $TIMESTAMP" >> db_backup.log
        $COMMAND_PATH
        STATUS="$?"
        status_check $DB $BACKUP_DIR $BACKUP_NAME $OLD_FILENAME $LEAST_DUMPSIZE $DUMP_NAME $STATUS
    }


    # This function takes backup of mysql database
    mysql_backup(){

    ###### Set Parameters ######
        DB=$DB2
        COMMAND_PATH="/usr/bin/mysqldump -u root -proot --all-databases"
        BACKUP_DIR="$DB-dumps"
        BACKUP_NAME="$BACKUP_DIR-$TIMESTAMP"
        OLD_FILENAME="$BACKUP_DIR-$OLD_TIMESTAMP"
        LEAST_DUMPSIZE="5"
        DUMP_NAME="mysqldump.sql"

    ###### Create MySQL Dump ######
        echo "[$DB]Creating $DB Dump on $TIMESTAMP" >> db_backup.log
        $COMMAND_PATH > $DUMP_NAME
        STATUS="$?"
        status_check $DB $BACKUP_DIR $BACKUP_NAME $OLD_FILENAME $LEAST_DUMPSIZE $DUMP_NAME $STATUS
    }

    # This function takes backup of redis database
    redis_backup(){

    ###### Set Parameters ######
        DB=$DB3
        COMMAND_PATH="/usr/bin/redis-cli save"
        BACKUP_DIR="$DB-dumps"
        BACKUP_NAME="$BACKUP_DIR-$TIMESTAMP"
        OLD_FILENAME="$BACKUP_DIR-$OLD_TIMESTAMP"
        LEAST_DUMPSIZE="5"
        DUMP_NAME="dump.rdb"


    ###### Create Redis Dump ######
        echo "[$DB]Creating $DB Dump on $TIMESTAMP" >> db_backup.log
        $COMMAND_PATH
        STATUS="$?"
        cp /home/centos/redis-3.2.5/dump.rdb .
        STATUS1="$?"
        if [ "$STATUS1" != "0" ];then
            FILE="FILE"
            echo "sendmail  with $STATUS ERROR" >> db_backup.log
            send_mail $FILE "ERROR" "File NOT Accessable, Process exit with STATUS: $STATUS"
        else
            status_check $DB $BACKUP_DIR $BACKUP_NAME $OLD_FILENAME $LEAST_DUMPSIZE $DUMP_NAME $STATUS
        fi
}


cat << EOM
        +---------------------------------------+
        |  This Script will take backup of all  |
        |   database and store backup in S3     |
        |  Bucket in a tar file and remove the  |
        |  previous backups [of 15 days before] |
        +---------------------------------------+         
EOM

sudo chown -R $USER /opt
DEST_DIR="/opt/backups"
mkdir -p $DEST_DIR
STATUS11="$?"
if [ "$STATUS11" != "0" ];then
    FILE="FILE"
    echo "[$FILE]sendmail  with $STATUS11 ERROR" >> db_backup.log
    send_mail $FILE "ERROR" "File NOT Accessable, Process exit with STATUS: $STATUS11"
else
    cd $DEST_DIR
    echo "creating backups in $DEST_DIR" >> db_backup.log
    if [ ! -f mongodb_backup.lock ];then
            touch mongodb_backup.lock
            mongodb_backup
            rm -rf mongodb_backup.lock
    else       
            echo "[$DB1]mongodb_backup.lock exists. Plz Check" >> db_backup.log
            send_mail $FILE "ERROR" "Mongodb File Lock exist"
    fi
    
    if [ ! -f mysql_backup.lock ];then
            touch mysql_backup.lock
            mysql_backup
            rm -rf mysql_backup.lock
    else
            echo "[$DB2]mysql_backup.lock exists. Plz Check" >> db_backup.log
            send_mail $FILE "ERROR" "MySQL File Lock exist"
    fi
    
    if [ ! -f redis_backup.lock ];then
            touch redis_backup.lock
            redis_backup
            rm -rf redis_backup.lock
    else       
            echo "[$DB3]redis_backup.lock exists. Plz Check" >> db_backup.log
            send_mail $FILE "ERROR" "Redis File Lock exist"
    fi
    
    if [ $flag == 3 ];then
	echo "success"
        echo "#####*****SUCCESS!!!*****#####" >> db_backup.log
        send_mail "Daily Backup" "SUCCESS" "Backup successfully taken"
    else
	echo "failed"
        echo "#####****FAILED!!!*****#####" >> db_backup.log
        send_mail "Daily Backup" "FAILED" "ERROR occured while taking backup please check.."
    fi
fi
cd -
