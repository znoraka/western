// ----------------------------------------------------------------------------
// Filename        : image_ppm.c
// Description     : Librairie universelle pour ICAR, lecture/Ecriture d'images PPM/PGM
// Created On      : Tue Mar 31 13:26:36 2005
// Revision        : Tue July 2016
// ----------------------------------------------------------------------------

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

// #define ALLOCATION(N,type) new type [N]   // pour C++ windows
//Flat Allocation
#define ALLOCATION(N,type) (type *)malloc(N*sizeof(type)) 
//Array Allocation
#define allocation_tableau(nom, type, nombre) \
if( (nom = (type*) calloc (nombre, sizeof(type) ) ) == NULL ) \
{\
 printf("\n Allocation dynamique impossible pour un pointeur-tableau \n");\
 exit(1);\
}

#define DESALLOCATION(pointeur) free(pointeur)   // pour C windows
// #define DESALLOCATION(pointeur) delete pointeur   // pour C++ windows

typedef unsigned char OCTET;

/*===Extract extension from file name========================================================================*/
void Extract_Ext(char* namefile)
{	
	char *pDot = strchr(namefile, '.');
	if(pDot!=NULL)
		*pDot = '\0';
}
/*===========================================================================*/

/*===If Commentaries exist in header========================================================================*/
void ignorer_commentaires(FILE * f)
{
  unsigned char c;
  while((c=fgetc(f)) == '#')
    while((c=fgetc(f)) != '\n');
  fseek(f, -sizeof(unsigned char), SEEK_CUR);
}
/*===========================================================================*/

/*==============================Extension non connue=============================================*/
//Determine PGM / PPM
void Format_image(char* nom_image_in, int* pformat)
{
	FILE *f_image;
	char format_img[2];

	f_image = fopen(nom_image_in,"rb");	
	fscanf(f_image, "%s", format_img);		//P5 / P6
	fclose(f_image);
	
	if(strncmp(format_img,"P5",2) == 0) 
		*pformat=1;
	else if(strncmp(format_img,"P6",2) == 0) 
		*pformat=2;		
	else 
	{
		printf("\nL'image %s n'est pas au format P5 ou P6\n", nom_image_in);
		*pformat=-1;	
		exit(EXIT_FAILURE);
	}	
}

/*====================Image PPM=======================================================*/
void ecrire_image_ppm(char  nom_image[], OCTET *pt_image, int nb_lignes, int nb_colonnes)
{
   FILE *f_image;
   int taille_image = 3*nb_colonnes * nb_lignes;

   if( (f_image = fopen(nom_image, "wb")) == NULL)
      {
	 printf("\nPas d'acces en ecriture sur l'image %s \n", nom_image);
	 exit(EXIT_FAILURE);
      }
   else
      {
	 fprintf(f_image,"P6\r") ;                               /*ecriture entete*/
	 fprintf(f_image,"%d %d\r255\r", nb_colonnes, nb_lignes) ;

	 if( (fwrite((OCTET*)pt_image, sizeof(OCTET), taille_image, f_image))
	     != (size_t)(taille_image))
	    {
	       printf("\nErreur d'ecriture de l'image %s \n", nom_image);
	       exit(EXIT_FAILURE);
	    }
	 fclose(f_image);
      }
}
/*===========================================================================*/
/*===========================================================================*/		
void lire_nb_lignes_colonnes_image_ppm(char nom_image[], int *nb_lignes, int *nb_colonnes)
{
   FILE *f_image;
   int max_grey_val;

   /* cf : l'entete d'une image .ppm : P6                   */
   /*				       nb_colonnes nb_lignes */
   /*    			       max_grey_val          */


   if( (f_image = fopen(nom_image, "rb")) == NULL)
      {
	 printf("\nPas d'acces en lecture sur l'image %s \n", nom_image);
	 exit(EXIT_FAILURE);
      }
   else
      {
	 fscanf(f_image, "P6 ");
	 ignorer_commentaires(f_image);
	 fscanf(f_image, "%d %d %d%*c", nb_colonnes, nb_lignes, &max_grey_val);
	 fclose(f_image);
      }
}
/*===========================================================================*/
/*===========================================================================*/
void lire_image_ppm(char  nom_image[], OCTET *pt_image, int taille_image)
{
   FILE *f_image;
   int  nb_colonnes, nb_lignes, max_grey_val;
   // taille_image=3*taille_image;

   if( (f_image = fopen(nom_image, "rb")) == NULL)
      {
	 printf("\nPas d'acces en lecture sur l'image %s \n", nom_image);
	 exit(EXIT_FAILURE);
      }
   else
      {
	fscanf(f_image, "P6 ");
	ignorer_commentaires(f_image);
	fscanf(f_image, "%d %d %d%*c",
	       &nb_colonnes, &nb_lignes, &max_grey_val); /*lecture entete*/

	 if( (fread((OCTET*)pt_image, sizeof(OCTET), taille_image, f_image))
	     !=  (size_t)(taille_image))
	    {
	       printf("\nErreur de lecture de l'image %s \n", nom_image);
	       exit(EXIT_FAILURE);
	    }
	 fclose(f_image);
      }
}
/*============================Image PGM===============================================*/
void ecrire_image_pgm(char  nom_image[], OCTET *pt_image, int nb_lignes, int nb_colonnes)
{
   FILE *f_image;
   int taille_image = nb_colonnes * nb_lignes;

   if( (f_image = fopen(nom_image, "wb")) == NULL)
      {
	 printf("\nPas d'acces en ecriture sur l'image %s \n", nom_image);
	 exit(EXIT_FAILURE);
      }
   else
      {
	 fprintf(f_image,"P5\r") ;                               /*ecriture entete*/
	 fprintf(f_image,"%d %d\r255\r", nb_colonnes, nb_lignes) ;

	 if( (fwrite((OCTET*)pt_image, sizeof(OCTET), taille_image, f_image))
	     != (size_t) taille_image)
	    {
	       printf("\nErreur de lecture de l'image %s \n", nom_image);
	       exit(EXIT_FAILURE);
	    }
	 fclose(f_image);
      }
}
/*===========================================================================*/
void lire_nb_lignes_colonnes_image_pgm(char nom_image[], int *nb_lignes, int *nb_colonnes)
{
   FILE *f_image;
   int max_grey_val;

   /* cf : l'entete d'une image .pgm : P5                    */
   /*				       nb_colonnes nb_lignes */
   /*    			       max_grey_val          */


   if( (f_image = fopen(nom_image, "rb")) == NULL)
      {
	 printf("\nPas d'acces en lecture sur l'image %s \n", nom_image);
	 exit(EXIT_FAILURE);
      }
   else
      {
	 fscanf(f_image, "P5 ");
	 ignorer_commentaires(f_image);
	 fscanf(f_image, "%d %d %d%*c", nb_colonnes, nb_lignes, &max_grey_val);
	 fclose(f_image);
      }
}
/*===========================================================================*/
/*===========================================================================*/
void lire_image_pgm(char  nom_image[], OCTET *pt_image, int taille_image)
{
   FILE *f_image;
   int  nb_colonnes, nb_lignes, max_grey_val;

   if( (f_image = fopen(nom_image, "rb")) == NULL)
      {
	 printf("\nPas d'acces en lecture sur l'image %s \n", nom_image);
	 exit(EXIT_FAILURE);
      }
   else
      {
	fscanf(f_image, "P5 ");
	ignorer_commentaires(f_image);
	fscanf(f_image, "%d %d %d%*c",
	       &nb_colonnes, &nb_lignes, &max_grey_val); /*lecture entete*/

	 if( (fread((OCTET*)pt_image, sizeof(OCTET), taille_image, f_image))
	     !=  (size_t) taille_image)
	    {
	       printf("\nErreur de lecture de l'image %s \n", nom_image);
	       exit(EXIT_FAILURE);
	    }
	 fclose(f_image);
      }
}
/*===========================================================================*/
/*===========================================================================*/
/*=========================Channel Red==================================================*/
void planR(OCTET *pt_image, OCTET *src, int taille_image){
   int i;
   for (i=0; i<taille_image; i++){
      pt_image[i]=src[3*i];
      }
   }
   
/*===========================================================================*/
/*============================Channel Green===============================================*/

void planV(OCTET *pt_image, OCTET *src, int taille_image){
   int i;
   for (i=0; i<taille_image; i++){
      pt_image[i]=src[3*i+1];
      }
   }   

/*===========================================================================*/
/*===========================Channel Bleu================================================*/
void planB(OCTET *pt_image, OCTET *src, int taille_image){
   int i;
   for (i=0; i<taille_image; i++){
      pt_image[i]=src[3*i+2];
      }
   }
   
/*===========================================================================*/   
/*===========================Ecriture à l'aveugle (Deprecated)================================================*/
//Si allocation taille PPM/PGM prédéfinie dans le main
void ecrire_image(char* nom_image, OCTET *pt_image, int taille_image, int nb_lignes,int nb_colonnes, int format)
{
	FILE *f_image;
	
	if( (f_image = fopen(nom_image, "wb")) == NULL)
	{
		printf("\nPas d'acces en ecriture sur l'image %s \n", nom_image);
		exit(EXIT_FAILURE);
	}
	else
	{
		if(format == 1) fprintf(f_image,"P5\n") ;/*ecriture entete*/
		else if(format == 2) fprintf(f_image,"P6\n") ;/*ecriture entete*/
	
		fprintf(f_image,"%d %d\n255\n", nb_colonnes, nb_lignes) ;
	
		if( (fwrite(pt_image, sizeof(OCTET), taille_image, f_image))
		!= (size_t) taille_image)
		{
			printf("\nErreur de lecture de l'image %s \n", nom_image);
			exit(EXIT_FAILURE);
		}
	}
	fclose(f_image);
}
/*===========================================================================*/
