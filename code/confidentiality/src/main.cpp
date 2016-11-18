#include <iostream>
#include <vector>
#include <algorithm>
#include <functional>
#include <fstream>
#include <cstdlib>
#include <ctime>
#include <map>
// #include <boost/math/distributions.hpp>

#include "image_ppm.h"

struct Image {
  const int GRAY = 0;
  const int RED = 0;
  const int GREEN = 1;
  const int BLUE = 2;

  int m = 1;
  
  std::vector<OCTET> data;
  int width;
  int height;

  Image(std::string path) {
    if(path.find(".ppm")) {
      m = 3;
      lire_nb_lignes_colonnes_image_ppm(const_cast<char*>(path.c_str()), &height, &width);
      data.resize(height * width * 3);
      lire_image_ppm(const_cast<char*>(path.c_str()), &data[0], data.size());
    } else if (path.find(".pgm")) {
      m = 1;
      lire_nb_lignes_colonnes_image_pgm(const_cast<char*>(path.c_str()), &height, &width);
      data.resize(height * width);
      lire_image_pgm(const_cast<char*>(path.c_str()), &data[0], data.size());
    } else {
      std::cout << "Must be a PNM file" << "\n";
      exit(-1);
    }
  }

  OCTET at(int i, int j, int channel = 0) {
    return data[i * width * m + j * m + channel];
  }
};



void psnr(Image& cover, Image& stego, std::ostream& stream = std::cout);
void npcr(Image& cover, Image& stego, std::ostream& stream = std::cout);
void uaci(Image& cover, Image& stego, std::ostream& stream = std::cout);
void correlationCoeff(Image& cover, Image& stego, bool horizontal = true, std::ostream& stream = std::cout);
void correlation(Image& cover, Image& stego, bool horizontal = true, std::ostream& stream = std::cout);
void chisquare(Image& cover, Image& stego, std::ostream& stream = std::cout);
void histogram(Image& cover, Image& stego, std::ostream& stream = std::cout);
void entropy(Image& cover, Image& stego, std::ostream& stream = std::cout);
std::vector<std::vector<int> > computeHistogram(Image& img);
double computeMean(std::vector<OCTET> values);
double computeVariance(std::vector<OCTET> values, double mean = 0);


std::vector<std::vector<int> > computeHistogram(Image& img) {
  std::vector<std::vector<int> > h;
  std::vector<int> r(256, 0);
  std::vector<int> g(256, 0);
  std::vector<int> b(256, 0);
  for (int i = 0; i < img.data.size(); i += img.m) {
    r[img.data[i]]++;
    if(img.m == 3) {
      g[img.data[i+1]]++;
      b[img.data[i+2]]++;
    }
  }
  h.push_back(r);
  if(img.m == 3) {
    h.push_back(g);
    h.push_back(b);
  }
  return h;
};

double computeMean(std::vector<OCTET> values) {
  long int sum = 0;
  for(auto i : values) {
    sum += i;
  }
  return (double)sum / (double)values.size();
}

double computeVariance(std::vector<OCTET> values, double mean) {
  if(mean == 0) mean = computeMean(values);

  double sum = 0;
  for(auto i : values) {
    sum += pow(i - mean, 2);
  }
  return sum / (double)values.size();
}

void psnr(Image& cover, Image& stego, std::ostream& stream) {
  double mse = 0;

  for (int i = 0; i < cover.data.size(); i++) {
    mse += pow(cover.data[i] - stego.data[i], 2);
  }
  mse /= cover.data.size();

  mse = 10 * log10(pow(255, 2) /  mse);

  stream << "psnr = " << mse << "\n";
}

void npcr(Image& cover, Image& stego, std::ostream& stream) {
  double sum = 0;
  
  for (int i = 0; i < cover.data.size(); i++) {
    sum +=  cover.data[i] != stego.data[i];
  }
  
  sum /= cover.data.size() * 0.01f;
  
  stream << "npcr = " << sum << "%\n";
}

void uaci(Image& cover, Image& stego, std::ostream& stream) {
  double sum = 0;
  
  for (int i = 0; i < cover.data.size(); i++) {
    sum +=  abs(cover.data[i] - stego.data[i]);
  }
  
  sum /= (255 * cover.data.size());
  sum *= 100;
  
  stream << "uaci = " << sum << "%\n";
}

void correlationCoeff(Image& cover, Image& stego, bool horizontal, std::ostream& stream) {
  auto rxy = [=](std::vector<int> indexes1, std::vector<int> indexes2, Image& image) {
    std::vector<OCTET> values1r, values1g, values1b;
    std::vector<OCTET> values2r, values2g, values2b;

    for (int i = 0; i < indexes1.size(); i++) {
      values1r.push_back(image.data[indexes1[i]]);
      values2r.push_back(image.data[indexes2[i]]);
      if(cover.m == 3) {
	values1g.push_back(image.data[indexes1[i]+1]);
	values2g.push_back(image.data[indexes2[i]+1]);
	values1b.push_back(image.data[indexes1[i]+2]);
	values2b.push_back(image.data[indexes2[i]+2]);
      }
    }

    double e1 = computeMean(values1r);
    double e2 = computeMean(values2r);
    double d1 = computeVariance(values1r, e1);
    double d2 = computeVariance(values2r, e2);

    int sum = 0;

    for (int i = 0; i < indexes1.size(); i++) {
      sum += (image.data[indexes1[i]] - e1) * (image.data[indexes2[i]] - e2);
    }
    sum = sum / (int) indexes1.size();
    return sum / (sqrt(d1) * sqrt(d2));
  };
  
  int samplesCount = std::max(500, (int)(cover.data.size() * 0.1));

  std::vector<int> samplesIndexes;
  std::vector<int> neighbors;

  for (int i = 0; i < samplesCount; i++) {
    samplesIndexes.push_back((std::rand() % (cover.data.size() / cover.m - cover.width)) * cover.m);
  }

  for (int i = 0; i < samplesCount; i++) {
    neighbors.push_back(horizontal ? samplesIndexes[i] + 1 + ((cover.m == 3)?2:0) : samplesIndexes[i] + cover.width * cover.m);
  }

  // stream << "correlation cover[" << ((horizontal) ? "horizontal" : "vertical") << "] = " << rxy(samplesIndexes, neighbors, cover) << std::endl;
  stream << "correlation stego[" << ((horizontal) ? "horizontal" : "vertical") << "] = " << rxy(samplesIndexes, neighbors, stego) << std::endl;
}

void correlation(Image& cover, Image& stego, bool horizontal, std::ostream& stream) {
  int samplesCount = std::max(500, (int)(cover.data.size() * 0.1));

  std::vector<int> samplesIndexes;
  std::vector<int> neighbors;

  for (int i = 0; i < samplesCount; i++) {
    samplesIndexes.push_back((std::rand() % (cover.data.size() / cover.m - cover.width)) * cover.m);
  }

  for (int i = 0; i < samplesCount; i++) {
    neighbors.push_back(horizontal ? samplesIndexes[i] + 1 + ((cover.m == 3)?2:0) : samplesIndexes[i] + cover.width * cover.m);
  }

  for (int i = 0; i < samplesCount; i++) {
    stream << (int) cover.data[samplesIndexes[i]] << " " << (int) cover.data[neighbors[i]] << " " << (int) stego.data[samplesIndexes[i]] << " " << (int) stego.data[neighbors[i]] << "\n";
    if(cover.m == 3) {
      stream << (int) cover.data[samplesIndexes[i+1]] << " " << (int) cover.data[neighbors[i+1]] << " " << (int) stego.data[samplesIndexes[i+1]] << " " << (int) stego.data[neighbors[i+1]] << "\n";
      stream << (int) cover.data[samplesIndexes[i+2]] << " " << (int) cover.data[neighbors[i+2]] << " " << (int) stego.data[samplesIndexes[i+2]] << " " << (int) stego.data[neighbors[i+2]] << "\n";
    }
  }
}

void histogram(Image& cover, Image& stego, std::ostream& stream) {
  auto coverHisto = computeHistogram(cover);
  auto stegoHisto = computeHistogram(stego);

  for (int i = 0; i < coverHisto[0].size(); i++) {
    if(stego.m == 3) stream << i << " " << (int)coverHisto[0][i] << " " << (int)coverHisto[1][i] << " " << (int)coverHisto[2][i] << " " << (int)stegoHisto[0][i] << (int)stegoHisto[1][i] << (int)stegoHisto[2][i] << "\n";
    else  stream << i << " " << (int)coverHisto[0][i] << " " << (int)stegoHisto[0][i] << "\n";
  }
}

// void chisquare(Image& cover, Image& stego, std::ostream& stream) {
//   auto criticalValue = [&](std::vector<int> histo, int nbValues) {
//     double p = 1.0 / 256.0;
//     double sum = 0;
//     std::vector<double> freqs;

//     for(auto i : histo) {
//       freqs.push_back(i / (double) nbValues);
//     }

//     for (int i = 0; i < 256; i++) {
//       sum += pow(freqs[i] - p, 2) / p;
//     }

//     return sum;
//   };

//   auto p_value = [](double criticalValue) {
//     boost::math::chi_squared mydist(255);
//     double p = boost::math::cdf(mydist, criticalValue);

//     return p;
//   };
  
//   auto coverHisto = computeHistogram(cover);
//   auto stegoHisto = computeHistogram(stego);

//   double coverCritValue = criticalValue(coverHisto, cover.data.size());
//   stream << "critical value[cover] = " << coverCritValue << "\n";

//   double stegoCritValue = criticalValue(stegoHisto, stego.data.size());
//   stream << "critical value[stego] = " << stegoCritValue << "\n";

//   stream << "chisquare[cover] = " << p_value(coverCritValue) << "\n";
// }

void entropy(Image& cover, Image& stego, std::ostream& stream) {
  auto f = [](Image& image) {
    auto e = [](std::vector<int> h, int len) {
      double sum = 0;

      for(auto i : h) {
	double freq = (double) i / len;
	sum += (i > 0) ? freq * std::log2(freq) : 0;
      }
      return -sum;
    };
    
    auto h = computeHistogram(image);
    double len = image.data.size() / image.m;
    double er = e(h[0], len);
    double eg = e(h[1], len);
    double eb = e(h[2], len);
    return (er + eg + eb) / 3.0;
  };

  // stream << "entropy[cover] = " << f(cover) << "\n";
  stream << "entropy[stego] = " << f(stego) << "\n";
}

int main(int argc, char **argv) {
  std::srand(std::time(0));

  Image cover(argv[1]);
  Image stego(argv[2]);

  if(cover.m != stego.m) {
    std::cout << "Images must be the same file format" << "\n";
    exit(-1);
  }

  std::ofstream corr("correlation.txt");
  std::ofstream chi("chisquare.txt");
  std::ofstream histo("histo.txt");

  psnr(cover, stego);
  npcr(cover, stego);
  uaci(cover, stego);
  // histogram(cover, stego, histo);
  correlationCoeff(cover, stego);
  correlationCoeff(cover, stego, false);
  // correlation(cover, stego, true, corr);
  // correlation(cover, stego, false, corr);
  // chisquare(cover, stego);
  entropy(cover, stego);

  corr.close();
  chi.close();
  histo.close();
}
