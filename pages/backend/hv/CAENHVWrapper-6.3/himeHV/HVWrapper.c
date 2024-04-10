#include <signal.h>
#ifdef UNIX
#include <sys/time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <termios.h>
#include <unistd.h>
#endif
#include <fcntl.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <ctype.h>
#include "HVWrapper.h"
#include "CAENHVWrapper.h"

//#define HIMEDEBUG

HV System[MAX_HVPS];

static int isInitialized = 0;


void freeMe(char* ptr){
	if(ptr != NULL){
		free(ptr);
	}
}

int noHVPS(void){	
	int i = 0;

	while( i != (MAX_HVPS - 1)){
		if(System[i].ID != -1) break;
		i++;
	}
	return ( ( i == MAX_HVPS - 1 ) ? 1 : 0 );
}

static int OneHVPS(void){	
	int i, j, k;

	for( i = 0, k = 0 ; i < (MAX_HVPS - 1) ; i++ )
		if( System[i].ID != -1 )
		{
			j = i;
			k++;
		}

	return ( ( k != 1 ) ? -1 : j );
}



void initSystem(int force){
	if(force == 0) if(isInitialized == 1) return;
	#ifdef HIMEDEBUG
	printf("[C] Initialize system.\n"); fflush(stdout);
	#endif
	for(int i = 0; i < MAX_HVPS ; i++ ){
		System[i].ID = -1;
	}
	isInitialized = 1;
}



const char* HVSystemLogin(char* user, char* passwd, char* ip){

	int i = 0;
	while( System[i].ID != -1 && i != (MAX_HVPS - 1)) i++;
	if( i == MAX_HVPS - 1 )
	{
		printf("\n");
		char* reply = "!!Too many connections";
		char* buf = strdup(reply);
		return buf;
	}
	
	int sysHndl = -1;
	CAENHVRESULT ret = CAENHV_InitSystem((CAENHV_SYSTEM_TYPE_t)2, LINKTYPE_TCPIP, ip, user, passwd, &sysHndl);
	// -- debug --
	#ifdef HIMEDEBUG
	printf("[C] HVSystemLogin:    i = %d    handle = %d    return = %d\n", i, sysHndl, ret);
	#endif
	// -----------

	char reply[300] = "";

	if( ret == CAENHV_OK ){
		while( System[i].ID != -1 ) i++;
		System[i].ID = ret;
		System[i].Handle = sysHndl;
		sprintf(reply, "%d", ret);
	}
	else{
		sprintf(reply, "!!%d", ret);
	}

	char *buf = strdup(reply);
	return buf;
}



const char* HVSystemLogout(){

	if( noHVPS() ){
		const char* reply = "!!There is no connection set up that could be closed now.";
		char* buf = strdup(reply);
		return buf;
	}

	int handle = -1;
	int i;
	if( ( i = OneHVPS() ) >= 0 ){
		handle = System[i].Handle;
	}

	CAENHVRESULT ret = CAENHV_DeinitSystem(handle);
	// -- debug --
	#ifdef HIMEDEBUG
	printf("[C] HVSystemLogout:    i = %d    handle = %d    return = %d\n", i, handle, ret);
	#endif
	// -----------

	char reply[300] = "";
	if( ret != CAENHV_OK ){
		sprintf(reply, "!!%d", ret);
	}
	
	if( ret == CAENHV_OK ){
		i = 0;
		while( System[i].Handle,handle ) i++;
		for( ; System[i].ID != -1; i++ ){
			System[i].ID = System[i+1].ID;
			System[i].Handle = System[i+1].Handle;
		}
	}

	char *buf = strdup(reply);
    return buf;
}



const char* HVGetCrateMap(){
	unsigned short	NrOfSl, *SerNumList, *NrOfCh;
	char			*ModelList, *DescriptionList;
	unsigned char	*FmwRelMinList, *FmwRelMaxList;
	CAENHVRESULT	ret;
	int				handle = -1;
	int				i;

	ModelList = NULL;
	DescriptionList = NULL;

	if( noHVPS() ){
		char* reply = "!!noHVPS";
		char* buf = strdup(reply);
		return buf;
	}

	if( ( i = OneHVPS() ) >= 0 )
		handle = System[i].Handle;

	char iChar[100] = "";
	sprintf(iChar, "[C] HVPS is i = %d\n", i);
	
	char reply[10000] = "";

	ret = CAENHV_GetCrateMap(handle, &NrOfSl, &NrOfCh, &ModelList, &DescriptionList, &SerNumList, &FmwRelMinList, &FmwRelMaxList );
	// -- debug --
	#ifdef HIMEDEBUG
	printf("[C] HVGetCrateMap:    i = %d    handle = %d    return = %d\n", i, handle, ret);
	#endif
	// -----------

	if( ret != CAENHV_OK ){
		sprintf(reply, "!!%d", ret);
		char* buf = strdup(reply);
		return buf;
	}

	if(!DescriptionList || !ModelList){
		char* reply = "!!DescriptionList or ModelList is NULL";
		char* buf = strdup(reply);
		return buf;
	}

	char *m = ModelList;
	char *d = DescriptionList;

	for(int i = 0; i < NrOfSl; i++ , m += strlen(m) + 1, d += strlen(d) + 1 ){
		if( *m == '\0' ){
			char tmp[50];
			sprintf(tmp, "----,,,,\n");
			strcat(reply, tmp);
		}
		else{
			char tmp[100];      
			sprintf(tmp, "%s,%s,%d,%d,%d.%d\n", m, d, NrOfCh[i], SerNumList[i], FmwRelMaxList[i], FmwRelMinList[i]);
			strcat(reply, tmp);
		}
	}

	CAENHV_Free(SerNumList);
	CAENHV_Free(ModelList);
	CAENHV_Free(DescriptionList);
	CAENHV_Free(FmwRelMinList);
	CAENHV_Free(FmwRelMaxList);
	CAENHV_Free(NrOfCh);
	
	char *buf = strdup(reply);
    return buf;
}



void freeLists(unsigned long type, float fParValList[], unsigned long lParValList[]){
	if( type == PARAM_TYPE_NUMERIC ){
		if( fParValList != NULL ){
			free(fParValList); 
		}
	}
	else{
		if( lParValList != NULL ){
			free(lParValList);
		}
	}
}



const char* throwError(int ret){
	char reply[100];
	sprintf(reply, "!!%d", ret);
	return strdup(reply);
}



const char* freeListsAndThrowError(int ret, unsigned long type, float fParValList[], unsigned long lParValList[]){
	freeLists(type, fParValList, lParValList);
	return throwError(ret);
}



const char* HVGetChParam(unsigned short Slot, unsigned short chStart, unsigned short chStop, char* ParName){

	char reply[800] = "";

	if( noHVPS() ){
		strcpy(reply, "!!noHVPS");
		char* buf = strdup(reply);
		return buf;
	}

	int i = -1, handle = -1;
	if( ( i = OneHVPS() ) >= 0 ){
		handle = System[i].Handle;
	}

	if(chStop == -1){
		chStop = chStart + 1;
	}

	unsigned short ChNum = chStop - chStart;
	unsigned short* ChList;
	ChList = malloc(ChNum * sizeof(unsigned short));
	
	for(int ch = chStart; ch < chStop; ch++){
		ChList[ch - chStart] = ch;
	}

	// Get fParValList or lParValList
	float			*fParValList = NULL;
	unsigned long	type, *lParValList = NULL;

	CAENHVRESULT ret = CAENHV_GetChParamProp(handle, Slot, ChList[0], ParName, "Type", &type);
	if( ret != CAENHV_OK ){
		if(ChList != NULL) free(ChList);
		return freeListsAndThrowError(ret, type, fParValList, lParValList);
	}

	/*
		TODO:

		The variable "type" is not set correctly set by CAENHV_GetChParamProp...
		It looks like empty memory is read...

		This function can access HV paramters of type float or long,
		and you have to make sure to use fParValList in the former case
		and lParValList in the latter.
	*/
	type = PARAM_TYPE_NUMERIC;
	
	if( type == PARAM_TYPE_NUMERIC ){
		fParValList = malloc(ChNum*sizeof(float));
		ret = CAENHV_GetChParam(handle, Slot, ParName, ChNum, ChList, fParValList);
	}
	else{
		lParValList = malloc(ChNum*sizeof(long));
		ret = CAENHV_GetChParam(handle, Slot, ParName, ChNum, ChList, lParValList);
	}

	// check & debug
	//printf("handle = %d\n", handle);
	//printf("slot = %d\n", Slot);
	//printf("ParName = %s\n", ParName);
	//printf("chlist[0] = %d\n", ChList[0]);
	//printf("type = %ld\n", type);
	//printf("param_type_num = %d\n",PARAM_TYPE_NUMERIC);

	// Use the above lists to get channel parameters
	if( ret != CAENHV_OK ){
		if(ChList != NULL) free(ChList);
		return freeListsAndThrowError(ret, type, fParValList, lParValList);
	}
	
	for(int iCh = 0; iCh < chStop - chStart; iCh++){
		char tmp[16];
		//if( type == PARAM_TYPE_NUMERIC ){
		if( 1 ){
			sprintf(tmp, "%10.2f", fParValList[iCh]);
		}
		else{
			sprintf(tmp, "%ld", lParValList[iCh]);
		}
		if( iCh < chStop - chStart - 1 ){
			strcat(tmp, ",");
		}
		strcat(reply, tmp);
	}

	if(ChList != NULL) free(ChList);
	freeLists(type, fParValList, lParValList);
	char* buf = strdup(reply);
	return buf;
}



const char* HVSetChParam(unsigned short Slot, unsigned short chStart, unsigned short chStop, char* ParName, float value_float, int value_int, unsigned long type_par){

	char reply[20] = "";

	if( noHVPS() ){
		strcpy(reply, "!!noHVPS");
		char* buf = strdup(reply);
		return buf;
	}

	int i;
	int handle = -1;
	if( ( i = OneHVPS() ) >= 0 )
		handle = System[i].Handle;

	unsigned short ChNum = chStop - chStart;

	unsigned short* ChList = malloc(ChNum * sizeof(unsigned short));

	for(int i = 0; i < ChNum; i++ ){
		ChList[i] = (unsigned short)i + chStart;
	}	 

	unsigned long type;

	CAENHVRESULT ret = CAENHV_GetChParamProp(handle, Slot, ChList[0], ParName, "Type", &type);
	
	if( ret != CAENHV_OK ){
		if(ChList != NULL) free(ChList);
		return throwError(ret);
	}
	
	/*
		See TODO in HVGetChParam
	*/
	//if( type == PARAM_TYPE_NUMERIC ){
	if( type_par == 0){
		ret = CAENHV_SetChParam(handle, Slot, ParName, ChNum, ChList, &value_float);
	}
	else{
		ret = CAENHV_SetChParam(handle, Slot, ParName, ChNum, ChList, &value_int);
	}

	if(ChList != NULL) free(ChList);

	if( ret != CAENHV_OK ){
		return throwError(ret);
	}

	char* buf = strdup(reply);
	return buf;
}