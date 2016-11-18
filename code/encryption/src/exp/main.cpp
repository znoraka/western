#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <ctime>
#include <sys/stat.h>
#include <sys/types.h>
#include <algorithm>

// #include "../lib/dirent.h"
#include "../image/Image.h"
// #include "parser.h"

// #define dirOut "/home/noe/Downloads/tmp/res/"

// #define dirImg "/home/noe/Downloads/tmp/nbase/"

#define qfIn 100
#define JPG ".jpg"
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
  struct stat st = {0};

  std::string dirOut = std::string(argv[1]);
  std::string dirImg = std::string(argv[2]);
  std::string keyString = std::string(argv[3]);
  int qf = std::stoi(std::string(argv[4]));

  cout << "dirout = " << dirOut << "\n";
  cout << "dirImg = " << dirImg << "\n";
  
  std::vector<std::string> params;
  std::string paramString;

  for (int i = 0; i < argc; i++) {
    params.push_back(std::string(argv[i]));
  }

  for(auto i : params) {
    cout << "param = " << i << "\n";
  }

  cout << "qf = " << qf << "\n";

  AC = paramExists("--ac", params);
  DC = paramExists("--dc", params);
  shuffleC = paramExists("--shuffle", params);
  FIBS = paramExists("--fibs", params);
  xorOp = paramExists("--xor", params);
  crcb = paramExists("--chrominance", params);
  lum = paramExists("--luminance", params);
    
  if (stat(dirOut.c_str(), &st) == -1)
    mkdir(dirOut.c_str(), 0777);
  
  unsigned long key = 435643135;	//seed parameter
  //string extIn = BMP;
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
	std::string tmpPath;
	ss.str("");

	if(AC) tmpPath += "ac_";
	if(DC) tmpPath += "dc_";
	if(shuffleC) tmpPath += "shuffle_";
	if(xorOp) tmpPath += "xor_";
	if(crcb) tmpPath += "chrominance_";
	if(lum) tmpPath += "luminance_";
	    
	ss<<dirOut<<tmpPath<<qf<<"_";

	/**********************************/
			
	ss<<inputImage<<JPG;
	string outputImageName=ss.str();
	ss.str("");

	ss << dirOut << tmpPath << qf << "_" << inputImage;

	string baseImage = ss.str();

	ss.str("");

	Image *img=new Image(rawpath,extIn);
	img->compress_JPG(outputImageName,qf,DC,AC,shuffleC,FIBS,xorOp,lum,crcb,key);
	delete img;
	//attack
	// ss<<dirQF<<inputImage<<qfT[qfa];
	// string att=ss.str();
	// ss.str("");
	// Image *imgA=new Image(outputImageName,JPG);
	// imgA->attackDC(att+".bmp",att);
	// delete imgA;
	//done
	string decodeCompress,recomp;
	    //path
	    ss.str("");
	    // ss<<dirQF<<inputImage<<qf<<"Cpy"<<JPG;	// ! si qfa = 6 erreur mais inutile
	    ss << baseImage << "Cpy" << JPG;
	    recomp=ss.str();
	    cout << "outputImage = " << outputImageName << "\n";
	    cout << "recomp = " << recomp << "\n";
	    Image *img2=new Image(outputImageName,JPG);
	    cout << "opened image" << "\n";
	    int newQf = img2->exportRecomp_JPG(recomp);
	    cout << "new qf = " << newQf << "\n";
	    delete img2;
	    //
	    ss.str("");
	    ss << baseImage << "Cpy_Decoded" << JPG;
	    // ss<<dirQF<<inputImage<<qf<<"Cpy_Decoded"<<JPG;
	    decodeCompress = ss.str();
	    Image *img3=new Image(recomp,JPG);//reopen recompress img
	    img3->cryting(decodeCompress,key);		//CRYPT //1 recompression ! mieux si lu dans le header
	    delete img3;
	  // }
	//   //Recompressions successives
	//   if(FIBS && iQF>0){
	//     //path
	//     ss.str("");
	//     ss<<dirOut<<"dir"<<qfT[qfa-1]<<"/"<<inputImage<<qfT[qfa]<<"Cpy"<<JPG;
	//     string previous=ss.str();
	//     cout<<"current: "<<outputImageName<<"    previous: "<<previous<<endl;
	//     //
	//     ss.str("");
	//     ss<<dirQF<<inputImage<<qfT[qfa+1]<<"CpySS"<<JPG;
	//     string sscomp=ss.str();
	//     startTime = clock();
	//     Image *img5=new Image(previous,JPG);
	//     img5->exportRecomp_JPG(sscomp);
	//     endTime = clock();
	//     clockTicksTaken = endTime - startTime;
	//     t4 = clockTicksTaken / (double) CLOCKS_PER_SEC;
	//     delete img5;
	//     ss.str("");
	//     ss<<dirQF<<inputImage<<qfT[qfa+1]<<"CpySS_Decoded"<<JPG;
	//     string ssdecode = ss.str();
	//     startTime = clock();
	//     Image *img6=new Image(sscomp,JPG);//reopen recompress img
	//     img6->cryting(ssdecode,key);	
	//     endTime = clock();
	//     clockTicksTaken = endTime - startTime;
	//     t5 = clockTicksTaken / (double) CLOCKS_PER_SEC;
	//     delete img6;
	//   }
	//   //decode
	ss.str("");
	// ss<<dirQF<<inputImage<<qf<<"_Decoded"<<JPG;
	ss << baseImage << "_Decoded" << JPG;

	string decodeOriginal = ss.str();
	Image *img4=new Image(outputImageName,JPG);//reopen original jpeg img
	img4->cryting(decodeOriginal,key);		//CRYPT
	delete img4;
	//attack
	// ss.str("");
	// ss<<dirQF<<inputImage<<qfT[qfa]<<"_Decoded";
	// att=ss.str();
	// ss.str("");
	// Image *imgA2=new Image(decodeOriginal,JPG);
	// imgA2->attackDC(att+".bmp",att);
	// delete imgA2;
	//done

	//   //STATS
	//   ss.str("");
	//   ss<<dirQF<<inputImage<<qfT[qfa]<<"STATS.txt";
	//   string stats=ss.str();
	//   //
	//   CImg<uchar> iR,i0,i1,i2,i3,i4,i3d,i3c;
	//   iR = CImg<uchar>(rawpath.c_str()); //raw
	//   i0 = CImg<uchar>(outputImageName.c_str()); //proposed chiffre
	//   //i1 = CImg<uchar>(outputImageNameBase.c_str()); //JPEG base
	//   i2 = CImg<uchar>(decodeOriginal.c_str()); //dechiffre
	//   if(iQF<6){
	//     i3 = CImg<uchar>(recomp.c_str()); //comp chiffre
	//     i4 = CImg<uchar>(decodeCompress.c_str()); //dechiffre comp
	//   }
	//   //
	//   //QUALITY
	//   int img_size = iR.width()*iR.height();
	//   ss_res<<qfT[qfa]<<" "<<getPsnrFrom(iR,i0)<<" "<<getBitSize(outputImageName,img_size)<<" "<<t0<<endl
	// 	  <<qfT[qfa]<<" "<<getPsnrFrom(iR,i2)<<" "<<getBitSize(decodeOriginal,img_size)<<" "<<t2<<endl;
	//   if(iQF<6){
	//     ss_res<<qfT[qfa+1]<<" "<<getPsnrFrom(iR,i3)<<" "<<getBitSize(recomp,img_size)<<" "<<t3<<endl
	// 	    <<qfT[qfa+1]<<" "<<getPsnrFrom(iR,i4)<<" "<<getBitSize(decodeCompress,img_size)<<" "<<t4<<endl;
	//   }
	//   //write
	//   ofstream nfile(stats.c_str(), ios::out | ios::trunc);
	//   if(nfile){
	//     nfile<<ss_res.str();
	//     nfile.close();
	//   }
	//   //
	//   ss_res.str("");
      }
    }
  }else {
    /* could not open directory */
    perror ("");
    return EXIT_FAILURE;
  }
  exit(0);
}
