#ifndef IMAGE_H
#define IMAGE_H

#include <string>
#include <iostream>
#include <vector>
#include <bitset>
#include <fstream>
#include <random>
#include <vector>
#include <algorithm>    // std::random_shuffle
#include <cstdlib>      // std::rand, std::srand

#define cimg_use_jpeg
#include "../lib/CImg.h"

#define DIM_BLOCK 8
#define uchar unsigned char
#define uint unsigned int

class Image{
public:
    Image(std::string,std::string);
	Image();
	~Image(void);
    //JPEG
	void setTable(int);
    void compress_JPG(std::string pathOut,int qf,bool dc,bool ac,bool shuffle,bool FIBS,bool xorOp,bool lum,bool crcb,unsigned long seed);
	void exportRecomp_JPG(std::string);
	void toMem(std::string path);
	void write_jpeg_file(std::string,jpeg_decompress_struct, jvirt_barray_ptr *);
	void write_jpeg_file(std::string);
    const uchar* data(const unsigned int, const unsigned int=0, const unsigned int=0, const unsigned int=0) const;
	//crypto
	void cryting(std::string,unsigned long key);
	short coding_xor(short val,int);
	short* getHuffmanCode(short val);
	short getHuffmanVal(short val,short size);
	short randomValue(short size);
	std::vector<std::vector<int>> orderV(std::vector<std::vector<int>>);
	//attack
	void attackDC(std::string,std::string);
	void export_dist(std::string,std::vector<std::vector<int>>);
private:
	//variables
	bool dc,ac,shuffle,FIBS,xorOp,crcb,lum,code,recomp,decode;
	//
    std::string path;
    cimg_library::CImg<uchar> img;
	unsigned int Q_variable[2][DIM_BLOCK*DIM_BLOCK];
    int qf;
    unsigned int width,height,depth;
    unsigned int _spectrum;
	std::mt19937_64 generator;//, gtest;
	//temp memory
	unsigned char *mem;
	unsigned long mem_size;
	//to export
	struct jpeg_decompress_struct dinfo;
	jvirt_barray_ptr *coeffs_array;
};
#endif  //IMAGE_H
