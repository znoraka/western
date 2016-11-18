#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <ctime>
#include <sys/stat.h>
#include <sys/types.h>
#include <algorithm>
#include <bitset>

#include "../image/Image.h"

#define qfIn 100
#define JPG ".jpeg"
#define PGM ".pgm"
#define BMP ".bmp"

bool AC = true;
bool DC = true;
bool shuffleC = true;
bool FIBS = false;
bool xorOp = true;
bool crcb = true;
bool lum = true;

// #define AC true
// #define DC true
// #define shuffle true //shuffle
// #define FIBS false //shuffle non 0
// #define xorOp true //xor
// #define crcb true //chrominance
// #define lum true //luminance

using namespace std;
using namespace cimg_library;


float getBitSize(string path,int nbpixel){
  size_t sz=0;
  std::FILE *const nfileB = fopen(path.c_str(),"rb");
  if(nfileB){
    fseek(nfileB, 0L, SEEK_END);
    sz = ftell(nfileB);
    fclose(nfileB);
  }
  return sz/(float)(nbpixel); //bits/pixels
}

float getPsnrFrom(CImg<uchar> imgO, CImg<uchar> img){
  return (float)imgO.PSNR(img);
}

bool paramExists(std::string param, std::vector<std::string> params) {
  return std::find(params.begin(), params.end(), param) != params.end();
}

int main(int argc, char *argv[]){
  std::string dirOut = std::string(argv[1]);
  std::string dirImg = std::string(argv[2]);

  auto f = [=](std::vector<std::string> params) {
    struct stat st = {0};
    
    AC = paramExists("ac", params);
    DC = paramExists("dc", params);
    shuffleC = paramExists("shuffle", params);
    FIBS = paramExists("fibs", params);
    xorOp = paramExists("xor", params);
    crcb = paramExists("chrominance", params);
    lum = paramExists("luminance", params);
    
    if (stat(dirOut.c_str(), &st) == -1)
      mkdir(dirOut.c_str(), 0777);
  
    unsigned long key = 435643135;	//seed parameter
    //string extIn = BMP;
    float qf=-1;
    int qfa=-1;
    float qfT[2] = {76,15};
    string dirQF="";
    double t0,t1,t2,t3,t4,t5,t6;
    clock_t startTime,endTime,clockTicksTaken;
    //LOOP all qf
    DIR *dir;
    struct dirent *ent;
    string ImgIn, extIn;
    if ((dir = opendir (dirImg.c_str())) != NULL) {
      while ((ent = readdir (dir)) != NULL) {
	printf ("%s\n", ent->d_name);
	ImgIn = ent->d_name;
	if(ImgIn != "." &&  ImgIn != ".."){ 
	  size_t fileExtPos = ImgIn.find_last_of(".");
	  if (fileExtPos != string::npos ){
	    extIn= ImgIn.substr(fileExtPos);
	    ImgIn= ImgIn.substr(0,fileExtPos);
	  }
	  for(int iQF=0;iQF<2;iQF++){ //0/7
	    qfa=iQF;
	    stringstream ss,ss_res;
	    ss<<dirImg<<ImgIn<<extIn;
	    string inputImage=ss.str();
	    //
	    string rawpath = inputImage;
	    //name
	    ss.str("");
	    ss.clear();
	    fileExtPos = inputImage.find_last_of(".");
	    if (fileExtPos != string::npos )
	      inputImage= inputImage.substr(0, fileExtPos);
	    string prefx ="";
	    fileExtPos = inputImage.find_last_of("/");
	    if (fileExtPos != string::npos ){
	      prefx= inputImage.substr(0, fileExtPos+1);
	      inputImage= inputImage.substr(fileExtPos+1);
	    }
	    //subdir

	    std::string tmpPath;

	    for(auto i : params) {
	      tmpPath += i + "_";
	    }
	    
	    ss<<dirOut<<tmpPath<<qfT[qfa]<<"_";
			
	    /**********************************/
			
	    ss<<inputImage<<JPG;
	    string outputImageName=ss.str();
	    ss.str("");
	    //export
	    startTime = clock();
	    Image *img=new Image(rawpath,extIn);
	    img->compress_JPG(outputImageName,qfa,DC,AC,shuffleC,FIBS,xorOp,lum,crcb,key);
	    endTime = clock();
	    clockTicksTaken = endTime - startTime;
	    t0 = clockTicksTaken / (double) CLOCKS_PER_SEC;
	    delete img;
	    string decodeCompress,recomp;
	    ss.str("");
	    ss<<dirQF<<inputImage<<qfT[qfa]<<"_Decoded"<<JPG;
	    string decodeOriginal = ss.str();
	    startTime = clock();
	    Image *img4=new Image(outputImageName,JPG);//reopen original jpeg img
	    img4->cryting(decodeOriginal,key);		//CRYPT
	    endTime = clock();
	    clockTicksTaken = endTime - startTime;
	    t4 = clockTicksTaken / (double) CLOCKS_PER_SEC;
	    delete img4;
	  }
	}
      }
    }
    
    closedir(dir);
    free(ent);
  };
  

  std::vector<std::string> paramsList = {"ac", "dc", "shuffle", "xor", "chrominance", "luminance"};
  const int size = paramsList.size();

  for (int i = 0; i < pow(2, paramsList.size()); i++) {
    std::bitset<6> b(i);
    std::vector<std::string> params;

    for (int j = 0; j < b.size(); j++) {
      if(b[j]) params.push_back(paramsList[j]);
    }

    f(params);
  }

  

  // for (int i = 0; i < argc; i++) {
  //   params.push_back(std::string(argv[i]));
  // }

  exit(0);
}
