#!/bin/bash
CWD=$1
MODEL=$2
x=$(basename $2)
NAME=${x%.*}
JAVA=$(which java)
RM=$(which rm)
MKDIR=$(which mkdir)
MEM=2048m

PATH=${CWD}/testtmp
DB_NAME=testdb
DB_PATH=${PATH}
DB_DEBUG=false
DB_TYPE=DERBY
CREATE_XML=true
CREATE_GRAPHVIZ=false
PART_STR="1::1:1"
RUNTIME_ENV="[c_master,d_master],[c_slave1,d_slave1,eth2,10.10.1.1,eth3,10.10.3.2]"
PORTAL_LINKS="c_slave1:eth2,topnet.net01.net1.r1.portal_10_1_3_0,c_slave1:eth3,topnet.net2.r5.portal_10_1_2_0"
OUT_DIR=${PATH}

JAR="${CWD}/../dist/jprime.jar"
OPS="-Xmx${MEM} -DDB_NAME=${DB_NAME} -DDB_PATH=${DB_PATH} -DDB_DEBUG=${DB_DEBUG} -DDB_TYPE=${DB_TYPE} -DCREATE_XML=${CREATE_XML} -DCREATE_GRAPHVIZ=${CREATE_GRAPHVIZ} -DPART_STR=${PART_STR} -DRUNTIME_ENV=${RUNTIME_ENV} -DPORTAL_LINKS=${PORTAL_LINKS} -DOUT_DIR=${OUT_DIR}"
CMD="${JAVA} ${OPS} -jar ${JAR} create ${NAME}.model ${MODEL}"

echo "Comping ${x}"
${MKDIR} -p ${PATH}
${RM} -rf ${PATH}/*.{_1.xml,tlv}
${CMD} &> ${MODEL}.comp.out
rv=$?
if [ "0" == "${rv}" ]
then
	#lets see if we can load up the associated xml
	CMD="${JAVA} ${OPS} -jar ${JAR} create ${NAME}.model_xml ${OUT_DIR}/${NAME}.model.xml"
	echo "\tComping extacted version of ${x}"
	${CMD} &> ${MODEL}.xml.comp.out
	rv=$?
	if [ "0" == "${rv}" ]
	then
		echo "PASS" > ${MODEL}.comp
	else
		echo "FAIL" > ${MODEL}.comp
	fi
else
	echo "FAIL" > ${MODEL}.comp
fi
exit 0
