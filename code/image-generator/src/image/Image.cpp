#include "Image.h"

using namespace cimg_library;
using namespace std;

Image::Image(string path,string ext){
  this->path=path;
  this->code = false;
  this->decode = true;
  if(ext==".jpeg"){	//OPEN JPEG for recompression
    Image::toMem(path);
  }else{				//OPEN img for crypto-compression
    this->img=CImg<uchar>(path.c_str());
    this->width=img.width();
    this->height=img.height();
    this->depth=img.depth();
    _spectrum = img.spectrum();
    mem = NULL;
    mem_size = 0;
  }
}

Image::Image(){
  this->path="";
  this->width=0;
  this->height=0;
  mem_size = 0;
}

Image::~Image(void){
  if(mem_size!=0)
    free(mem);
}

void Image::setTable(int q){	//OUR TABLE
  float Qfactor[7] = {0.0625,0.125,0.25,0.5,1,2,4};
  double factor=Qfactor[q];
  int BlockWidth=DIM_BLOCK;
  int BlockHeight=DIM_BLOCK;
  int Q_baseL[DIM_BLOCK][DIM_BLOCK]={16,16,16,16,16,32,48,48,16,16,16,16,16,48,48,48,16,16,16,16,32,48,64,48,16,16,16,16,48,80,80,48,16,16,32,48,64,96,96,64,16,32,48,64,80,96,112,80,48,64,64,80,96,112,112,96,64,80,80,96,112,96,96,96};
  int Q_baseC[DIM_BLOCK][DIM_BLOCK]={16,16,32,48,96,96,96,96,16,16,32,64,96,96,96,96,32,32,64,96,96,96,96,96,48,64,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96};
  uint tmp;
  for(int i=0;i<BlockWidth;i++){
    for(int j=0;j<BlockHeight;j++){
      int p=i*BlockWidth+j;
      tmp=(uint)ceil(Q_baseL[i][j]*factor);
      if(tmp>255)
	tmp=255;
      Q_variable[0][p]= tmp;
      tmp=(uint)ceil(Q_baseC[i][j]*factor);
      if(tmp>255)
	tmp=255;
      Q_variable[1][p]= tmp;
    }
  }
	
}

void Image::toMem(std::string path){
  FILE * infile;
  if ((infile = fopen(path.c_str(), "rb")) == NULL) {
    fprintf(stderr, "can't open %s\n", path.c_str());
    exit(-1);
  }
  // obtain file size:
  fseek (infile , 0 , SEEK_END);
  mem_size = ftell (infile);
  rewind (infile);
  // allocate memory to contain the whole file:
  mem = (unsigned char*) malloc (sizeof(char)*mem_size);
  fread(mem,1,mem_size,infile);
  fclose( infile );
}

void Image::compress_JPG(std::string pathOut,int qf,bool dc,bool ac,bool shuffle,bool FIBS,bool xorOp,bool lum,bool crcb,unsigned long seed){
  this->dc = dc;
  this->ac = ac;
  this->shuffle = shuffle;
  this->xorOp = xorOp;
  this->crcb = crcb;
  this->lum = lum;
  this->FIBS = FIBS;
  this->code = true;
  this->decode = false;
  unsigned int dimbuf = 0;
  J_COLOR_SPACE colortype = JCS_RGB;
  switch (_spectrum) {
  case 1 : dimbuf = 1; colortype = JCS_GRAYSCALE; break;
  case 3 : dimbuf = 3; colortype = JCS_RGB; break;
  }
  // Call libjpeg functions
  struct jpeg_compress_struct cinfo;
  struct jpeg_error_mgr jerr;
  cinfo.err = jpeg_std_error(&jerr);
  jpeg_create_compress(&cinfo);
  jpeg_mem_dest(&cinfo, &mem, &mem_size);
  cinfo.image_width = width;
  cinfo.image_height = height;
  cinfo.input_components = dimbuf;
  cinfo.in_color_space = colortype;
  jpeg_set_defaults(&cinfo);
  cinfo.progressive_mode=false;
  cinfo.optimize_coding=false; // default huffman
  setTable(qf);
  int ci=0;//change QUANTIZATION TABLE
  int bound;
  if(_spectrum==1){ //grey
    bound = 1;
  }else{	//color
    bound = 2;
  }
  for(ci;ci<bound;ci++){
    cinfo.quant_tbl_ptrs[ci] = jpeg_alloc_quant_table((j_common_ptr) &cinfo);
    JQUANT_TBL* quant_ptr = cinfo.quant_tbl_ptrs[ci];
    for (int i = 0; i < DIM_BLOCK*DIM_BLOCK; i++) {
      quant_ptr->quantval[i] = Q_variable[ci][i];
    }
  }
  //ALLOCATE
  jpeg_start_compress(&cinfo,TRUE);
  JSAMPROW row_pointer[1];
  CImg<uchar> buffer((unsigned long)width*dimbuf);

  while (cinfo.next_scanline<cinfo.image_height) {
    uchar *ptrd = buffer._data;
    // Fill pixel buffer
    switch (_spectrum) {
    case 1 : { // Greyscale images
      const uchar *ptr_g = data(0, cinfo.next_scanline);
      for (unsigned int b = 0; b<cinfo.image_width; b++){
	*(ptrd++) = (unsigned char)*(ptr_g++);
      }
    } break;
    case 3 : { // RGB images
      const uchar *ptr_r = data(0,cinfo.next_scanline,0,0);
      const uchar *ptr_g = data(0,cinfo.next_scanline,0,1);
      const uchar *ptr_b = data(0,cinfo.next_scanline,0,2);
      for (unsigned int b = 0; b<cinfo.image_width; ++b) {
	*(ptrd++) = (unsigned char)*(ptr_r++);
	*(ptrd++) = (unsigned char)*(ptr_g++);
	*(ptrd++) = (unsigned char)*(ptr_b++);
      }
    }
    }
    *row_pointer = buffer._data;
    jpeg_write_scanlines(&cinfo,row_pointer,1);
  }
  //all pixels added in pgm 
  jpeg_comp_master *t = cinfo.master;
  jpeg_finish_compress(&cinfo);
  //done
  jpeg_destroy_compress(&cinfo);
  cryting(pathOut,seed);
}


void Image::cryting(std::string pathOut,unsigned long seed){
  //random
  std::srand (seed);
  generator.seed(seed);
  //decompress mem for DCT 
  struct jpeg_decompress_struct cinfo;
  struct jpeg_error_mgr jerr;
  const unsigned int max_marker_length = 0xffff;
  cinfo.err = jpeg_std_error(&jerr);
  jpeg_create_decompress(&cinfo);  
  jpeg_mem_src(&cinfo, mem,mem_size);
  jpeg_save_markers(&cinfo,JPEG_COM,max_marker_length);
  (void) jpeg_read_header(&cinfo, TRUE);
  recomp = 0;
  if(!code){ //decode soit qf soit recompress read header
    recomp = 0;
    dc= 0;
    ac= 0;
    shuffle= 0;
    xorOp= 0;
    crcb= 0;
    lum= 0;
    code= 0;
    FIBS =0;
    jpeg_saved_marker_ptr mptr;
    bool maj=false;
    JOCTET* comment;
    unsigned int marker_length;
    for (mptr = cinfo.marker_list; NULL != mptr; mptr = mptr->next){
      if (mptr->marker == JPEG_COM){
	marker_length = mptr->data_length;
	comment = new JOCTET[marker_length];
	memcpy(comment,mptr->data,marker_length);
	maj =true;
      }
    }
    if(maj){
      recomp = (comment[0]=='1')? true:false;
      dc= (comment[1]=='1')? true:false;
      ac= (comment[2]=='1')? true:false;
      shuffle= (comment[3]=='1')? true:false;
      xorOp= (comment[4]=='1')? true:false;
      crcb= (comment[5]=='1')? true:false;
      lum= (comment[6]=='1')? true:false;
      FIBS= (comment[7]=='1')? true:false;
      delete comment;
      //cout<<"		"<<recomp<<" "<<dc<<" "<<ac<<" "<<shuffle<<" "<<xorOp<<" "<<crcb<<" "<<lum<<endl;
    }
  }
  _spectrum = cinfo.num_components;
  //recomp
  jvirt_barray_ptr *coeffs_array = jpeg_read_coefficients(&cinfo);
  //values:
  int ci = 0; // between 0 and number of image component
  int by = 0; // between 0 and compptr_one->height_in_blocks
  int bx = 0; // between 0 and compptr_one->width_in_blocks
  int bi = 0; // between 0 and 64 (8x8)
  int blck_size = 64;
  int start_Coef = 0;
  if(!ac)
    blck_size = 1;
  if(!dc)
    start_Coef = 1;
  int cp=0;
  if(!lum)
    cp=1;
  int rp=_spectrum;
  if(!crcb)
    rp=1;
  JCOEFPTR blockptr;
  JBLOCKARRAY buffer;
  jpeg_component_info* compptr_one;

  //generate indices if shuffle + garder coef DC + AC non nul de taille >1
  // Create
  //std::vector<std::vector<std::vector<int>>> indices(3, vector<vector<int>>(64)); //1 vector for each frequency
  std::vector<std::vector<std::vector<int> > > indices (3, vector<vector<int> > (64)); 
  std::vector<std::vector<std::vector<short> > > cdct(3, vector<vector<short> > (64));
  std::vector<std::vector<int> > cpt(3,vector<int>(64));
  //
  //deshuffle
  if((shuffle && !code) || (code && shuffle && !xorOp)){ //false decode
    for(ci=cp;ci<rp;ci++){
      compptr_one = cinfo.comp_info+ci;
      for(by=0;by<compptr_one->height_in_blocks;by++){
	buffer = (cinfo.mem->access_virt_barray)((j_common_ptr)&cinfo, coeffs_array[ci], by, (JDIMENSION)1, FALSE);
	for(bx=0;bx<compptr_one->width_in_blocks;bx++){
	  blockptr = buffer[0][bx];
	  for(bi=start_Coef;bi<blck_size;bi++){	//coefs
	    if(FIBS){
	      cdct[ci][bi].push_back(blockptr[bi]);
	      indices[ci][bi].push_back(cpt[ci][bi]);
	      cpt[ci][bi]++;
	    }else{
	      if(recomp==0){//chiffre
		if(!FIBS && blockptr[bi]!=0 &&  blockptr[bi]!=-1 && blockptr[bi]!=1){
		  cdct[ci][bi].push_back(blockptr[bi]);
		  indices[ci][bi].push_back(cpt[ci][bi]);
		  cpt[ci][bi]++;
		}
	      }else{
		if(!FIBS && blockptr[bi]!=0){
		  cdct[ci][bi].push_back(blockptr[bi]);
		  indices[ci][bi].push_back(cpt[ci][bi]);
		  cpt[ci][bi]++;
		}
	      }
	    }
	  }
	}
      }
    }
  }
  if(shuffle && !code){ //false decode
    for(int k=0;k<_spectrum;k++){	//pas optimisé
      for(int i=start_Coef;i<blck_size;i++){
	std::random_shuffle(indices[k][i].begin(), indices[k][i].end());
      }
    }
    //
    std::vector<std::vector<int>> cpt2(3,vector<int>(64));
    std::vector<std::vector<std::vector<int>>> res(3, vector<vector<int>>(64));
    for(int k=0;k<_spectrum;k++){
      res[k] = orderV(indices[k]);
    }
    for(ci=cp;ci<rp;ci++){
      compptr_one = cinfo.comp_info+ci;
      for(by=0;by<compptr_one->height_in_blocks;by++){
	buffer = (cinfo.mem->access_virt_barray)((j_common_ptr)&cinfo, coeffs_array[ci], by, (JDIMENSION)1, FALSE);
	for(bx=0;bx<compptr_one->width_in_blocks;bx++){
	  blockptr = buffer[0][bx];
	  for(bi=start_Coef;bi<blck_size;bi++){//coefs
	    if(FIBS){
	      blockptr[bi]  = cdct[ci][bi][res[ci][bi][cpt2[ci][bi]]];
	      cpt2[ci][bi]++;
	    }else{
	      if(recomp==0){//chiffre
		if(!FIBS && blockptr[bi]!=0 && blockptr[bi]!=1 && blockptr[bi]!=-1 ){ // pas 1 -1 pour deshuffle sinon les recompressé pas deshuffle
		  blockptr[bi]  = cdct[ci][bi][res[ci][bi][cpt2[ci][bi]]];
		  cpt2[ci][bi]++;
		}
	      }else{
		if(!FIBS && blockptr[bi]!=0){ // recompress coef size 1 were size 2
		  blockptr[bi]  = cdct[ci][bi][res[ci][bi][cpt2[ci][bi]]];
		  cpt2[ci][bi]++;
		}
	      }
	    }
	  }
	}
      }
    }
  }
  //CHIFFREMENT XOR
  if(xorOp){
    for(ci=cp;ci<rp;ci++){
      compptr_one = cinfo.comp_info+ci;
      for(by=0;by<compptr_one->height_in_blocks;by++){
	buffer = (cinfo.mem->access_virt_barray)((j_common_ptr)&cinfo, coeffs_array[ci], by, (JDIMENSION)1, FALSE);
	for(bx=0;bx<compptr_one->width_in_blocks;bx++){
	  blockptr = buffer[0][bx];
	  for(bi=start_Coef;bi<blck_size;bi++){	//AC ou DC
						//if(blockptr[bi]!=0 && ((!recomp&& blockptr[bi]!=-1024) || (recomp&& blockptr[bi]!=-512))){	//chiffre que les coefs non nuls et pas de taille 1 : /2 ->0 //original 1024 codé 11 bits pb donc pas de chiffrement
	    if(blockptr[bi]!=0){	
	      if(recomp==0){//chiffre
		if(blockptr[bi]!=1 && blockptr[bi]!=-1){//pas de chiffrement des coefs de taille 1
		  blockptr[bi]=coding_xor(blockptr[bi],recomp);
		}
	      }else{	//dechiffre //dechiffrement des coefs de taille 1
		blockptr[bi]=coding_xor(blockptr[bi],recomp);
	      }
	    }
	    if(code){//chiffre
	      if(FIBS){
		cdct[ci][bi].push_back(blockptr[bi]);
		indices[ci][bi].push_back(cpt[ci][bi]);
		cpt[ci][bi]++;
	      }else{
		if(blockptr[bi]!=0 &&  blockptr[bi]!=-1 && blockptr[bi]!=1){
		  cdct[ci][bi].push_back(blockptr[bi]);
		  indices[ci][bi].push_back(cpt[ci][bi]);
		  cpt[ci][bi]++;
		}
	      }
	    }
	  }
	}
      }
    }
  }
  //CHIFFREMENT XOR DONE
  //shuffle
  if(shuffle && code){
    for(int k=0;k<_spectrum;k++){	//pas optimisé
      for(int i=start_Coef;i<blck_size;i++){
	std::random_shuffle (indices[k][i].begin(), indices[k][i].end());
      }
    }
    std::vector<std::vector<int>> cpt2(3,std::vector<int>(64));
    for(ci=cp;ci<rp;ci++){
      compptr_one = cinfo.comp_info+ci;
      for(by=0;by<compptr_one->height_in_blocks;by++){
	buffer = (cinfo.mem->access_virt_barray)((j_common_ptr)&cinfo, coeffs_array[ci], by, (JDIMENSION)1, FALSE);
	for(bx=0;bx<compptr_one->width_in_blocks;bx++){
	  blockptr = buffer[0][bx];
	  for(bi=start_Coef;bi<blck_size;bi++){//AC
	    if(FIBS){
	      blockptr[bi]  = cdct[ci][bi][indices[ci][bi][cpt2[ci][bi]]];
	      cpt2[ci][bi]++;
	    }else{
	      if(blockptr[bi]!=0 && blockptr[bi]!=1 && blockptr[bi]!=-1 ){ // pas 1 -1 pour deshuffle sinon les recompressé pas deshuffle
		blockptr[bi]  = cdct[ci][bi][indices[ci][bi][cpt2[ci][bi]]];
		cpt2[ci][bi]++;
	      }
	    }
	  }
	}
      }
    }
  }
  //
  free(mem);
  mem_size = 0; 
  //copy to mem
  write_jpeg_file(pathOut, cinfo, coeffs_array);
}


//SHUFFLE
std::vector<std::vector<int>> Image::orderV(std::vector<std::vector<int>>v){
  std::vector<std::vector<int>> res(v.size(),std::vector<int>());
  for(int j=0;j<v.size();j++){
    res[j].reserve(v[j].size());
    for(int i=0;i<v[j].size();i++){
      res[j][v[j][i]]=i;
    }
  }
  return res;
}


//CHIFFREMENT
short Image::randomValue(short size){
  unsigned short k=0;	
  std::uniform_int_distribution<int> distribution(0, 1);
  for (int i = 0; i < size; i++){
    k = k | distribution(generator);
    if(i<size-1){
      k = k<<1;
    }
  }
  return k;
}

short Image::coding_xor(short val,int recomp){
  short* hufC = getHuffmanCode(val);
  short k = randomValue(hufC[0]+recomp);
  k=k>>recomp;
  unsigned short cval = k ^ hufC[1];
  cval = getHuffmanVal(cval,hufC[0]);	//last bit xor ^
  delete[] hufC;
  return cval;
}

short Image::getHuffmanVal(short val,short size){
  short sign = val>>(size-1);
  short mask = 0xFFFF>>(16-size);
  if(sign==0){
    val = val^mask;
    val=-val;
  }
  return val;
}

short* Image::getHuffmanCode(short val){ //0 return size 1 !
  short* hufC = new short[2];
  hufC[0]=0;	//size
  hufC[1]=0; //bin value
  //size
  int s=1;
  while(hufC[0]==0){//max range [-1024, 1023] libjpeg
    int p = std::pow(2.0,s);
    int bmax = (std::pow(2.0,s)-1);
    int bmin = -bmax;
    if(val>=bmin && val<=bmax){	//dans l'intervalle des valeurs de taille s
      hufC[0]=s;
    }
    s++;
  }
  //value valeur absolue inverse si neg
  short mask = 0xFFFF>>(16-hufC[0]);
  if(val<0){
    val=-val;
    hufC[1] = val^mask;	//xor inverse
  }else{
    hufC[1]=val;
  }
  return hufC;
}


void Image::write_jpeg_file(std::string outname,jpeg_decompress_struct in_cinfo, jvirt_barray_ptr *coeffs_array){
  struct jpeg_compress_struct cinfo;
  struct jpeg_error_mgr jerr;
  FILE * infile;
  if ((infile = fopen(outname.c_str(), "wb")) == NULL) {
    fprintf(stderr, "can't open %s\n", outname.c_str());
    exit(-1);
  }
  cinfo.err = jpeg_std_error(&jerr);
  jpeg_create_compress(&cinfo);
  jpeg_stdio_dest(&cinfo, infile);

  j_compress_ptr cinfo_ptr = &cinfo;
  jpeg_copy_critical_parameters((j_decompress_ptr)&in_cinfo,cinfo_ptr);
  //change values
  //change QUANTIZATION TABLE
  if(recomp==1 && !decode){
    int ci=0;
    uint tmp;
    int bound;
    if(_spectrum==1){ //grey
      bound = 1;
    }else{	//color
      bound = 2;
    }
    for(ci;ci<bound;ci++){
      cinfo.quant_tbl_ptrs[ci] = jpeg_alloc_quant_table((j_common_ptr) &cinfo);
      JQUANT_TBL* quant_ptr = cinfo.quant_tbl_ptrs[ci];
      for (int i = 0; i < DIM_BLOCK*DIM_BLOCK; i++) {
	tmp = Q_variable[ci][i]*2;
	if(tmp>255)
	  tmp=255;
	quant_ptr->quantval[i] = tmp;
      }
    }
  }
  jpeg_write_coefficients(cinfo_ptr, coeffs_array);
  //Com
  JOCTET comment[8];
  comment[0] = (recomp)?'1':'0'; //recomp
  comment[1] = (dc)?'1':'0'; //DC
  comment[2] = (ac)?'1':'0'; //AC
  comment[3] = (shuffle)?'1':'0'; //shuffle
  comment[4] = (xorOp)?'1':'0'; //xorOp
  comment[5] = (crcb)?'1':'0'; //crcb
  comment[6] = (lum)?'1':'0'; //lum
  comment[7] = (FIBS)?'1':'0'; //lum
  jpeg_write_marker(&cinfo, JPEG_COM, comment,8);
  //
  jpeg_finish_compress( &cinfo );
  jpeg_destroy_compress( &cinfo );
  fclose( infile );
}

void Image::write_jpeg_file(std::string outname){	//mem to file
  FILE * infile;
  if ((infile = fopen(outname.c_str(), "wb")) == NULL) {
    fprintf(stderr, "can't open %s\n", outname.c_str());
    exit(-1);
  }
  fwrite((char*)mem,sizeof(char), mem_size,infile);
  fclose( infile );
  free(mem);
  mem_size =0; 
}


void Image::exportRecomp_JPG(std::string pathOut){
  recomp = 1;
  this->decode = false;
  //load
  struct jpeg_decompress_struct cinfo;
  struct jpeg_error_mgr jerr;
  const unsigned int max_marker_length = 0xffff;
  cinfo.err = jpeg_std_error(&jerr);
  jpeg_create_decompress(&cinfo);
  jpeg_mem_src(&cinfo, mem,mem_size);
  jpeg_save_markers(&cinfo,JPEG_COM,max_marker_length);
  (void) jpeg_read_header(&cinfo, TRUE);
  //copy header
  dc= 0;
  ac= 0;
  shuffle= 0;
  xorOp= 0;
  crcb= 0;
  lum= 0;
  code= 0;
  FIBS =0;
  jpeg_saved_marker_ptr mptr;
  bool maj=false;
  JOCTET* comment;
  unsigned int marker_length;
  for (mptr = cinfo.marker_list; NULL != mptr; mptr = mptr->next){
    if (mptr->marker == JPEG_COM){
      marker_length = mptr->data_length;
      comment = new JOCTET[marker_length];
      memcpy(comment,mptr->data,marker_length);
      maj =true;
    }
  }
  if(maj){
    dc= (comment[1]=='1')? true:false;
    ac= (comment[2]=='1')? true:false;
    shuffle= (comment[3]=='1')? true:false;
    xorOp= (comment[4]=='1')? true:false;
    crcb= (comment[5]=='1')? true:false;
    lum= (comment[6]=='1')? true:false;
    FIBS= (comment[7]=='1')? true:false;
    delete comment;
  }
  _spectrum = cinfo.num_components;
  //copy table
  int n=0;
  int bound;
  if(_spectrum==1){ //grey
    bound = 1;
  }else{	//color
    bound = 2;
  }
  for(n;n<bound;n++){
    JQUANT_TBL* quant_ptr = cinfo.quant_tbl_ptrs[n];
    for (int i = 0; i < DIM_BLOCK*DIM_BLOCK; i++) {
      Q_variable[n][i] = quant_ptr->quantval[i];
    }
  }
  //recomp
  jvirt_barray_ptr *coeffs_array = jpeg_read_coefficients(&cinfo);
  //values:
  int ci = 0; // between 0 and number of image component
  int by = 0; // between 0 and compptr_one->height_in_blocks
  int bx = 0; // between 0 and compptr_one->width_in_blocks
  int bi = 0; // between 0 and 64 (8x8)
  //coefs divisés par 2
  JCOEFPTR blockptr;
  JBLOCKARRAY buffer;
  jpeg_component_info* compptr_one;
  for(ci;ci<_spectrum;ci++){
    compptr_one = cinfo.comp_info+ci;
    for(by=0;by<compptr_one->height_in_blocks;by++){
      buffer = (cinfo.mem->access_virt_barray)((j_common_ptr)&cinfo, coeffs_array[ci], by, (JDIMENSION)1, FALSE);
      for(bx=0;bx<compptr_one->width_in_blocks;bx++){
	blockptr = buffer[0][bx];
	for(bi=0;bi<64;bi++){
	  blockptr[bi]/=2;
	}
      }
    }
  }
  //export
  write_jpeg_file(pathOut, cinfo, coeffs_array);
  jpeg_finish_decompress( &cinfo );
  jpeg_destroy_decompress( &cinfo );
}


const uchar* Image::data(const unsigned int x, const unsigned int y, const unsigned int z, const unsigned int c) const {
  return img._data + x + y*width + z*(unsigned long)width*height + c*(unsigned long)width*height*depth;
}

void Image::attackDC(std::string pathOut,std::string name){
  struct jpeg_decompress_struct cinfo;
  struct jpeg_error_mgr jerr;
  cinfo.err = jpeg_std_error(&jerr);
  jpeg_create_decompress(&cinfo);
  jpeg_mem_src(&cinfo, mem,mem_size);
  (void) jpeg_read_header(&cinfo, TRUE);
  _spectrum = cinfo.num_components;
  width = cinfo.image_width;
  height = cinfo.image_height;
  int lwidth = width/8;
  int lheight = height/8;
  jvirt_barray_ptr *coeffs_array = jpeg_read_coefficients(&cinfo);
  //values:
  int ci = 0; // between 0 and number of image component
  int by = 0; // between 0 and compptr_one->height_in_blocks
  int bx = 0; // between 0 and compptr_one->width_in_blocks
  int bi = 0; // between 0 and 64 (8x8)
  vector<vector<vector<int>>> nimg;
  nimg.resize(lheight);
  for (int i = 0; i < lheight; ++i){
    nimg[i].resize(lwidth);
    for (int j = 0; j < lwidth; ++j)
      nimg[i][j].resize(_spectrum);
  }

  int cpt;
  vector<int> sl(_spectrum,0);
  std::vector<std::vector<std::vector<int>>> cdct(3, vector<vector<int>>(64));
  JCOEFPTR blockptr;
  JBLOCKARRAY buffer;
  jpeg_component_info* compptr_one;
  for(ci;ci<_spectrum;ci++){
    compptr_one = cinfo.comp_info+ci;
    for(by=0;by<compptr_one->height_in_blocks;by++){
      buffer = (cinfo.mem->access_virt_barray)((j_common_ptr)&cinfo, coeffs_array[ci], by, (JDIMENSION)1, FALSE);
      for(bx=0;bx<compptr_one->width_in_blocks;bx++){
	blockptr = buffer[0][bx];
	cpt=0;
	for(bi=0;bi<64;bi++){
	  cdct[ci][bi].push_back(blockptr[bi]);
	  if(blockptr[bi]!=0)
	    cpt++;

	  //test
	  if(ci==0){
	    blockptr[bi] = 0;
	    /*if(bi>0)
	      blockptr[bi] = 0;
	      else{
	      if(!(by==0 && bx==0))
	      blockptr[bi] = 0;
	      }*/
	  }
	}
	nimg[by][bx][ci] = cpt;
	sl[ci]+=cpt;
	//tc[ci].push_back(cpt);
      }
    }
  }
  //test
  write_jpeg_file(name+"_color.jpeg",cinfo, coeffs_array);
  //
  jpeg_finish_decompress( &cinfo );
  jpeg_destroy_decompress( &cinfo );
  //percentage
  //for(int i=0;i<_spectrum;i++){
  //	std::sort(tc[i].begin(),tc[i].end());
  //}
  //range
  for(int i=0;i<_spectrum;i++){
    sl[i]/=(lheight*lwidth);//average
    //sl[i] = tc[i][int(0.9*tc.size())];
  }
  //new image
  _spectrum = 1;//lum
  CImg<int> myImage(lwidth,lheight,1,_spectrum);
  for(int k=0;k<_spectrum;k++){
    for(int i=0;i<lwidth;i++){
      for(int j=0;j<lheight;j++){
	myImage(i,j,k) = (nimg[j][i][k]>sl[k])?0:255;
      }
    }
  }
  myImage.save_bmp(pathOut.c_str());
  //save dist function
  // string pathFile = name+"lum.txt";
  // export_dist(pathFile,cdct[0]);
  // pathFile = name+"cr.txt";
  // export_dist(pathFile,cdct[1]);
  // pathFile = name+"cb.txt";
  // export_dist(pathFile,cdct[2]);

	

}

void Image::export_dist(std::string pathFile,std::vector<std::vector<int>> v){
  ofstream nfile(pathFile.c_str(), ios::out | ios::trunc);
  if(nfile){
    for(int i=0;i<v.size();i++){
      for(int j=0;j<v[i].size()-1;j++){
	nfile<<v[i][j]<<",";
      }
      nfile<<v[i][v[i].size()-1]<<endl;
    }
    nfile.close();
  }
}
