#include "iGraphics.h"
#include<unistd.h>
#include<time.h>

void homepage();
int hmpage=1;
void instruction();
int ins=0;
bool musicon=true;

void cluepage();
int clue=0;
void level1();
int l1=0;
void showSoil();
void winpage();
int win=0;

void cluepage2(); 
int clue2=0;
void level2();
int l2=0;
void showSoil2();
void winpage2();
int win2=0; 

void cluepage3();
int clue3=0;
void level3();
int l3=0;
void showSoil3();
void winpage3();
int win3=0; 


void overpage();
int over=0; 

void pause();
int p1=0,p2=0,p3=0;

int x = 0, y = 0, r = 20;
int life=150; 
 
int a[43],b[43];
int c=1;
int sidx=1;

void onblock(int p[], int q[])  
{
    for(int i=0; i<25; i++)
	{
		 p[i] = (p[i]/24)*24;        // placing the snake on per block of soil
		 q[i] = (q[i]/30)*30;
	}
}

void spawn()
{
	for(int i=0;i<25;i++)
	{
		a[i]=rand()%576;
		b[i]=rand()%360;
	}
	onblock(a,b);
	a[25]=576;b[25]=360; a[26]=288;b[26]=360; a[27]=576;b[27]=180; a[28]=288;b[28]=180; a[29]=0;b[29]=180; a[30]=0,b[30]=0; 
	a[31]=288;b[31]=0; a[32]=432;b[32]=270; a[33]=144;b[33]=270; a[34]=144;b[34]=90; a[35]=432;b[35]=90;
	a[36]=144,b[36]=30, a[37]=432,b[37]=30; a[38]=480;b[38]=60; a[39]=576;b[39]=90; a[40]=504;b[40]=330; a[41]=72;b[41]=330; a[42]=72;b[42]=60;
}

char bi[325][40]= {"image\\00_back2.png","image\\01_back2.png","image\\02_back2.png","image\\03_back2.png","image\\04_back2.png","image\\05_back2.png","image\\06_back2.png","image\\07_back2.png","image\\08_back2.png","image\\09_back2.png","image\\10_back2.png","image\\11_back2.png","image\\12_back2.png","image\\13_back2.png","image\\14_back2.png","image\\15_back2.png","image\\16_back2.png","image\\17_back2.png","image\\18_back2.png","image\\19_back2.png","image\\20_back2.png","image\\21_back2.png","image\\22_back2.png","image\\23_back2.png","image\\24_back2.png","image\\25_back2.png","image\\26_back2.png","image\\27_back2.png","image\\28_back2.png","image\\29_back2.png","image\\30_back2.png","image\\31_back2.png","image\\32_back2.png","image\\33_back2.png","image\\34_back2.png","image\\35_back2.png","image\\36_back2.png","image\\37_back2.png","image\\38_back2.png","image\\39_back2.png","image\\40_back2.png","image\\41_back2.png","image\\42_back2.png","image\\43_back2.png","image\\44_back2.png","image\\45_back2.png","image\\46_back2.png","image\\47_back2.png","image\\48_back2.png","image\\49_back2.png","image\\50_back2.png","image\\51_back2.png","image\\52_back2.png","image\\53_back2.png","image\\54_back2.png","image\\55_back2.png","image\\56_back2.png","image\\57_back2.png","image\\58_back2.png","image\\59_back2.png","image\\60_back2.png","image\\61_back2.png","image\\62_back2.png","image\\63_back2.png","image\\64_back2.png","image\\65_back2.png","image\\66_back2.png","image\\67_back2.png","image\\68_back2.png","image\\69_back2.png","image\\70_back2.png","image\\71_back2.png","image\\72_back2.png","image\\73_back2.png","image\\74_back2.png","image\\75_back2.png","image\\76_back2.png","image\\77_back2.png","image\\78_back2.png","image\\79_back2.png","image\\80_back2.png","image\\81_back2.png","image\\82_back2.png","image\\83_back2.png","image\\84_back2.png","image\\85_back2.png","image\\86_back2.png","image\\87_back2.png","image\\88_back2.png","image\\89_back2.png","image\\90_back2.png","image\\91_back2.png","image\\92_back2.png","image\\93_back2.png","image\\94_back2.png","image\\95_back2.png","image\\96_back2.png","image\\97_back2.png","image\\98_back2.png","image\\99_back2.png","image\\100_back2.png","image\\101_back2.png","image\\102_back2.png","image\\103_back2.png","image\\104_back2.png","image\\105_back2.png","image\\106_back2.png","image\\107_back2.png","image\\108_back2.png","image\\109_back2.png","image\\110_back2.png","image\\111_back2.png","image\\112_back2.png","image\\113_back2.png","image\\114_back2.png","image\\115_back2.png","image\\116_back2.png","image\\117_back2.png","image\\118_back2.png","image\\119_back2.png","image\\120_back2.png","image\\121_back2.png","image\\122_back2.png","image\\123_back2.png","image\\124_back2.png","image\\125_back2.png","image\\126_back2.png","image\\127_back2.png","image\\128_back2.png","image\\129_back2.png","image\\130_back2.png","image\\131_back2.png","image\\132_back2.png","image\\133_back2.png","image\\134_back2.png","image\\135_back2.png","image\\136_back2.png","image\\137_back2.png","image\\138_back2.png","image\\139_back2.png","image\\140_back2.png","image\\141_back2.png","image\\142_back2.png","image\\143_back2.png","image\\144_back2.png","image\\145_back2.png","image\\146_back2.png","image\\147_back2.png","image\\148_back2.png","image\\149_back2.png","image\\150_back2.png","image\\151_back2.png","image\\152_back2.png","image\\153_back2.png","image\\154_back2.png","image\\155_back2.png","image\\156_back2.png","image\\157_back2.png","image\\158_back2.png","image\\159_back2.png","image\\160_back2.png","image\\161_back2.png","image\\162_back2.png","image\\163_back2.png","image\\164_back2.png","image\\165_back2.png","image\\166_back2.png","image\\167_back2.png","image\\168_back2.png","image\\169_back2.png","image\\170_back2.png","image\\171_back2.png","image\\172_back2.png","image\\173_back2.png","image\\174_back2.png","image\\175_back2.png","image\\176_back2.png","image\\177_back2.png","image\\178_back2.png","image\\179_back2.png","image\\180_back2.png","image\\181_back2.png","image\\182_back2.png","image\\183_back2.png","image\\184_back2.png","image\\185_back2.png","image\\186_back2.png","image\\187_back2.png","image\\188_back2.png","image\\189_back2.png","image\\190_back2.png","image\\191_back2.png","image\\192_back2.png","image\\193_back2.png","image\\194_back2.png","image\\195_back2.png","image\\196_back2.png","image\\197_back2.png","image\\198_back2.png","image\\199_back2.png","image\\200_back2.png","image\\201_back2.png","image\\202_back2.png","image\\203_back2.png","image\\204_back2.png","image\\205_back2.png","image\\206_back2.png","image\\207_back2.png","image\\208_back2.png","image\\209_back2.png","image\\210_back2.png","image\\211_back2.png","image\\212_back2.png","image\\213_back2.png","image\\214_back2.png","image\\215_back2.png","image\\216_back2.png","image\\217_back2.png","image\\218_back2.png","image\\219_back2.png","image\\220_back2.png","image\\221_back2.png","image\\222_back2.png","image\\223_back2.png","image\\224_back2.png","image\\225_back2.png","image\\226_back2.png","image\\227_back2.png","image\\228_back2.png","image\\229_back2.png","image\\230_back2.png","image\\231_back2.png","image\\232_back2.png","image\\233_back2.png","image\\234_back2.png","image\\235_back2.png","image\\236_back2.png","image\\237_back2.png","image\\238_back2.png","image\\239_back2.png","image\\240_back2.png","image\\241_back2.png","image\\242_back2.png","image\\243_back2.png","image\\244_back2.png","image\\245_back2.png","image\\246_back2.png","image\\247_back2.png","image\\248_back2.png","image\\249_back2.png","image\\250_back2.png","image\\251_back2.png","image\\252_back2.png","image\\253_back2.png","image\\254_back2.png","image\\255_back2.png","image\\256_back2.png","image\\257_back2.png","image\\258_back2.png","image\\259_back2.png","image\\260_back2.png","image\\261_back2.png","image\\262_back2.png","image\\263_back2.png","image\\264_back2.png","image\\265_back2.png","image\\266_back2.png","image\\267_back2.png","image\\268_back2.png","image\\269_back2.png","image\\270_back2.png","image\\271_back2.png","image\\272_back2.png","image\\273_back2.png","image\\274_back2.png","image\\275_back2.png","image\\276_back2.png","image\\277_back2.png","image\\278_back2.png","image\\279_back2.png","image\\280_back2.png","image\\281_back2.png","image\\282_back2.png","image\\283_back2.png","image\\284_back2.png","image\\285_back2.png","image\\286_back2.png","image\\287_back2.png","image\\288_back2.png","image\\289_back2.png","image\\290_back2.png","image\\291_back2.png","image\\292_back2.png","image\\293_back2.png","image\\294_back2.png","image\\295_back2.png","image\\296_back2.png","image\\297_back2.png","image\\298_back2.png","image\\299_back2.png","image\\300_back2.png","image\\301_back2.png","image\\302_back2.png","image\\303_back2.png","image\\304_back2.png","image\\305_back2.png","image\\306_back2.png","image\\307_back2.png","image\\308_back2.png","image\\309_back2.png","image\\310_back2.png","image\\311_back2.png","image\\312_back2.png","image\\313_back2.png","image\\314_back2.png","image\\315_back2.png","image\\316_back2.png","image\\317_back2.png","image\\318_back2.png","image\\319_back2.png","image\\320_back2.png","image\\321_back2.png","image\\322_back2.png","image\\323_back2.png","image\\324_back2.png"};
char minar[6][15]={"image\\c11.png","image\\c12.png","image\\c10.png","image\\c14.png","image\\c15.png","image\\c13.png"};

char snake[2][30]={"image\\snakeA.png","image\\snakeB.png"};
int idx=0;
bool stand=true;


char bib[325][40]= {"image2\\00_soil2.png","image2\\01_soil2.png","image2\\02_soil2.png","image2\\03_soil2.png","image2\\04_soil2.png","image2\\05_soil2.png","image2\\06_soil2.png","image2\\07_soil2.png","image2\\08_soil2.png","image2\\09_soil2.png","image2\\10_soil2.png","image2\\11_soil2.png","image2\\12_soil2.png","image2\\13_soil2.png","image2\\14_soil2.png","image2\\15_soil2.png","image2\\16_soil2.png","image2\\17_soil2.png","image2\\18_soil2.png","image2\\19_soil2.png","image2\\20_soil2.png","image2\\21_soil2.png","image2\\22_soil2.png","image2\\23_soil2.png","image2\\24_soil2.png","image2\\25_soil2.png","image2\\26_soil2.png","image2\\27_soil2.png","image2\\28_soil2.png","image2\\29_soil2.png","image2\\30_soil2.png","image2\\31_soil2.png","image2\\32_soil2.png","image2\\33_soil2.png","image2\\34_soil2.png","image2\\35_soil2.png","image2\\36_soil2.png","image2\\37_soil2.png","image2\\38_soil2.png","image2\\39_soil2.png","image2\\40_soil2.png","image2\\41_soil2.png","image2\\42_soil2.png","image2\\43_soil2.png","image2\\44_soil2.png","image2\\45_soil2.png","image2\\46_soil2.png","image2\\47_soil2.png","image2\\48_soil2.png","image2\\49_soil2.png","image2\\50_soil2.png","image2\\51_soil2.png","image2\\52_soil2.png","image2\\53_soil2.png","image2\\54_soil2.png","image2\\55_soil2.png","image2\\56_soil2.png","image2\\57_soil2.png","image2\\58_soil2.png","image2\\59_soil2.png","image2\\60_soil2.png","image2\\61_soil2.png","image2\\62_soil2.png","image2\\63_soil2.png","image2\\64_soil2.png","image2\\65_soil2.png","image2\\66_soil2.png","image2\\67_soil2.png","image2\\68_soil2.png","image2\\69_soil2.png","image2\\70_soil2.png","image2\\71_soil2.png","image2\\72_soil2.png","image2\\73_soil2.png","image2\\74_soil2.png","image2\\75_soil2.png","image2\\76_soil2.png","image2\\77_soil2.png","image2\\78_soil2.png","image2\\79_soil2.png","image2\\80_soil2.png","image2\\81_soil2.png","image2\\82_soil2.png","image2\\83_soil2.png","image2\\84_soil2.png","image2\\85_soil2.png","image2\\86_soil2.png","image2\\87_soil2.png","image2\\88_soil2.png","image2\\89_soil2.png","image2\\90_soil2.png","image2\\91_soil2.png","image2\\92_soil2.png","image2\\93_soil2.png","image2\\94_soil2.png","image2\\95_soil2.png","image2\\96_soil2.png","image2\\97_soil2.png","image2\\98_soil2.png","image2\\99_soil2.png","image2\\100_soil2.png","image2\\101_soil2.png","image2\\102_soil2.png","image2\\103_soil2.png","image2\\104_soil2.png","image2\\105_soil2.png","image2\\106_soil2.png","image2\\107_soil2.png","image2\\108_soil2.png","image2\\109_soil2.png","image2\\110_soil2.png","image2\\111_soil2.png","image2\\112_soil2.png","image2\\113_soil2.png","image2\\114_soil2.png","image2\\115_soil2.png","image2\\116_soil2.png","image2\\117_soil2.png","image2\\118_soil2.png","image2\\119_soil2.png","image2\\120_soil2.png","image2\\121_soil2.png","image2\\122_soil2.png","image2\\123_soil2.png","image2\\124_soil2.png","image2\\125_soil2.png","image2\\126_soil2.png","image2\\127_soil2.png","image2\\128_soil2.png","image2\\129_soil2.png","image2\\130_soil2.png","image2\\131_soil2.png","image2\\132_soil2.png","image2\\133_soil2.png","image2\\134_soil2.png","image2\\135_soil2.png","image2\\136_soil2.png","image2\\137_soil2.png","image2\\138_soil2.png","image2\\139_soil2.png","image2\\140_soil2.png","image2\\141_soil2.png","image2\\142_soil2.png","image2\\143_soil2.png","image2\\144_soil2.png","image2\\145_soil2.png","image2\\146_soil2.png","image2\\147_soil2.png","image2\\148_soil2.png","image2\\149_soil2.png","image2\\150_soil2.png","image2\\151_soil2.png","image2\\152_soil2.png","image2\\153_soil2.png","image2\\154_soil2.png","image2\\155_soil2.png","image2\\156_soil2.png","image2\\157_soil2.png","image2\\158_soil2.png","image2\\159_soil2.png","image2\\160_soil2.png","image2\\161_soil2.png","image2\\162_soil2.png","image2\\163_soil2.png","image2\\164_soil2.png","image2\\165_soil2.png","image2\\166_soil2.png","image2\\167_soil2.png","image2\\168_soil2.png","image2\\169_soil2.png","image2\\170_soil2.png","image2\\171_soil2.png","image2\\172_soil2.png","image2\\173_soil2.png","image2\\174_soil2.png","image2\\175_soil2.png","image2\\176_soil2.png","image2\\177_soil2.png","image2\\178_soil2.png","image2\\179_soil2.png","image2\\180_soil2.png","image2\\181_soil2.png","image2\\182_soil2.png","image2\\183_soil2.png","image2\\184_soil2.png","image2\\185_soil2.png","image2\\186_soil2.png","image2\\187_soil2.png","image2\\188_soil2.png","image2\\189_soil2.png","image2\\190_soil2.png","image2\\191_soil2.png","image2\\192_soil2.png","image2\\193_soil2.png","image2\\194_soil2.png","image2\\195_soil2.png","image2\\196_soil2.png","image2\\197_soil2.png","image2\\198_soil2.png","image2\\199_soil2.png","image2\\200_soil2.png","image2\\201_soil2.png","image2\\202_soil2.png","image2\\203_soil2.png","image2\\204_soil2.png","image2\\205_soil2.png","image2\\206_soil2.png","image2\\207_soil2.png","image2\\208_soil2.png","image2\\209_soil2.png","image2\\210_soil2.png","image2\\211_soil2.png","image2\\212_soil2.png","image2\\213_soil2.png","image2\\214_soil2.png","image2\\215_soil2.png","image2\\216_soil2.png","image2\\217_soil2.png","image2\\218_soil2.png","image2\\219_soil2.png","image2\\220_soil2.png","image2\\221_soil2.png","image2\\222_soil2.png","image2\\223_soil2.png","image2\\224_soil2.png","image2\\225_soil2.png","image2\\226_soil2.png","image2\\227_soil2.png","image2\\228_soil2.png","image2\\229_soil2.png","image2\\230_soil2.png","image2\\231_soil2.png","image2\\232_soil2.png","image2\\233_soil2.png","image2\\234_soil2.png","image2\\235_soil2.png","image2\\236_soil2.png","image2\\237_soil2.png","image2\\238_soil2.png","image2\\239_soil2.png","image2\\240_soil2.png","image2\\241_soil2.png","image2\\242_soil2.png","image2\\243_soil2.png","image2\\244_soil2.png","image2\\245_soil2.png","image2\\246_soil2.png","image2\\247_soil2.png","image2\\248_soil2.png","image2\\249_soil2.png","image2\\250_soil2.png","image2\\251_soil2.png","image2\\252_soil2.png","image2\\253_soil2.png","image2\\254_soil2.png","image2\\255_soil2.png","image2\\256_soil2.png","image2\\257_soil2.png","image2\\258_soil2.png","image2\\259_soil2.png","image2\\260_soil2.png","image2\\261_soil2.png","image2\\262_soil2.png","image2\\263_soil2.png","image2\\264_soil2.png","image2\\265_soil2.png","image2\\266_soil2.png","image2\\267_soil2.png","image2\\268_soil2.png","image2\\269_soil2.png","image2\\270_soil2.png","image2\\271_soil2.png","image2\\272_soil2.png","image2\\273_soil2.png","image2\\274_soil2.png","image2\\275_soil2.png","image2\\276_soil2.png","image2\\277_soil2.png","image2\\278_soil2.png","image2\\279_soil2.png","image2\\280_soil2.png","image2\\281_soil2.png","image2\\282_soil2.png","image2\\283_soil2.png","image2\\284_soil2.png","image2\\285_soil2.png","image2\\286_soil2.png","image2\\287_soil2.png","image2\\288_soil2.png","image2\\289_soil2.png","image2\\290_soil2.png","image2\\291_soil2.png","image2\\292_soil2.png","image2\\293_soil2.png","image2\\294_soil2.png","image2\\295_soil2.png","image2\\296_soil2.png","image2\\297_soil2.png","image2\\298_soil2.png","image2\\299_soil2.png","image2\\300_soil2.png","image2\\301_soil2.png","image2\\302_soil2.png","image2\\303_soil2.png","image2\\304_soil2.png","image2\\305_soil2.png","image2\\306_soil2.png","image2\\307_soil2.png","image2\\308_soil2.png","image2\\309_soil2.png","image2\\310_soil2.png","image2\\311_soil2.png","image2\\312_soil2.png","image2\\313_soil2.png","image2\\314_soil2.png","image2\\315_soil2.png","image2\\316_soil2.png","image2\\317_soil2.png","image2\\318_soil2.png","image2\\319_soil2.png","image2\\320_soil2.png","image2\\321_soil2.png","image2\\322_soil2.png","image2\\323_soil2.png","image2\\324_soil2.png"};

char bic[325][40]= {"image3\\00_soil3.png","image3\\01_soil3.png","image3\\02_soil3.png","image3\\03_soil3.png","image3\\04_soil3.png","image3\\05_soil3.png","image3\\06_soil3.png","image3\\07_soil3.png","image3\\08_soil3.png","image3\\09_soil3.png","image3\\10_soil3.png","image3\\11_soil3.png","image3\\12_soil3.png","image3\\13_soil3.png","image3\\14_soil3.png","image3\\15_soil3.png","image3\\16_soil3.png","image3\\17_soil3.png","image3\\18_soil3.png","image3\\19_soil3.png","image3\\20_soil3.png","image3\\21_soil3.png","image3\\22_soil3.png","image3\\23_soil3.png","image3\\24_soil3.png","image3\\25_soil3.png","image3\\26_soil3.png","image3\\27_soil3.png","image3\\28_soil3.png","image3\\29_soil3.png","image3\\30_soil3.png","image3\\31_soil3.png","image3\\32_soil3.png","image3\\33_soil3.png","image3\\34_soil3.png","image3\\35_soil3.png","image3\\36_soil3.png","image3\\37_soil3.png","image3\\38_soil3.png","image3\\39_soil3.png","image3\\40_soil3.png","image3\\41_soil3.png","image3\\42_soil3.png","image3\\43_soil3.png","image3\\44_soil3.png","image3\\45_soil3.png","image3\\46_soil3.png","image3\\47_soil3.png","image3\\48_soil3.png","image3\\49_soil3.png","image3\\50_soil3.png","image3\\51_soil3.png","image3\\52_soil3.png","image3\\53_soil3.png","image3\\54_soil3.png","image3\\55_soil3.png","image3\\56_soil3.png","image3\\57_soil3.png","image3\\58_soil3.png","image3\\59_soil3.png","image3\\60_soil3.png","image3\\61_soil3.png","image3\\62_soil3.png","image3\\63_soil3.png","image3\\64_soil3.png","image3\\65_soil3.png","image3\\66_soil3.png","image3\\67_soil3.png","image3\\68_soil3.png","image3\\69_soil3.png","image3\\70_soil3.png","image3\\71_soil3.png","image3\\72_soil3.png","image3\\73_soil3.png","image3\\74_soil3.png","image3\\75_soil3.png","image3\\76_soil3.png","image3\\77_soil3.png","image3\\78_soil3.png","image3\\79_soil3.png","image3\\80_soil3.png","image3\\81_soil3.png","image3\\82_soil3.png","image3\\83_soil3.png","image3\\84_soil3.png","image3\\85_soil3.png","image3\\86_soil3.png","image3\\87_soil3.png","image3\\88_soil3.png","image3\\89_soil3.png","image3\\90_soil3.png","image3\\91_soil3.png","image3\\92_soil3.png","image3\\93_soil3.png","image3\\94_soil3.png","image3\\95_soil3.png","image3\\96_soil3.png","image3\\97_soil3.png","image3\\98_soil3.png","image3\\99_soil3.png","image3\\100_soil3.png","image3\\101_soil3.png","image3\\102_soil3.png","image3\\103_soil3.png","image3\\104_soil3.png","image3\\105_soil3.png","image3\\106_soil3.png","image3\\107_soil3.png","image3\\108_soil3.png","image3\\109_soil3.png","image3\\110_soil3.png","image3\\111_soil3.png","image3\\112_soil3.png","image3\\113_soil3.png","image3\\114_soil3.png","image3\\115_soil3.png","image3\\116_soil3.png","image3\\117_soil3.png","image3\\118_soil3.png","image3\\119_soil3.png","image3\\120_soil3.png","image3\\121_soil3.png","image3\\122_soil3.png","image3\\123_soil3.png","image3\\124_soil3.png","image3\\125_soil3.png","image3\\126_soil3.png","image3\\127_soil3.png","image3\\128_soil3.png","image3\\129_soil3.png","image3\\130_soil3.png","image3\\131_soil3.png","image3\\132_soil3.png","image3\\133_soil3.png","image3\\134_soil3.png","image3\\135_soil3.png","image3\\136_soil3.png","image3\\137_soil3.png","image3\\138_soil3.png","image3\\139_soil3.png","image3\\140_soil3.png","image3\\141_soil3.png","image3\\142_soil3.png","image3\\143_soil3.png","image3\\144_soil3.png","image3\\145_soil3.png","image3\\146_soil3.png","image3\\147_soil3.png","image3\\148_soil3.png","image3\\149_soil3.png","image3\\150_soil3.png","image3\\151_soil3.png","image3\\152_soil3.png","image3\\153_soil3.png","image3\\154_soil3.png","image3\\155_soil3.png","image3\\156_soil3.png","image3\\157_soil3.png","image3\\158_soil3.png","image3\\159_soil3.png","image3\\160_soil3.png","image3\\161_soil3.png","image3\\162_soil3.png","image3\\163_soil3.png","image3\\164_soil3.png","image3\\165_soil3.png","image3\\166_soil3.png","image3\\167_soil3.png","image3\\168_soil3.png","image3\\169_soil3.png","image3\\170_soil3.png","image3\\171_soil3.png","image3\\172_soil3.png","image3\\173_soil3.png","image3\\174_soil3.png","image3\\175_soil3.png","image3\\176_soil3.png","image3\\177_soil3.png","image3\\178_soil3.png","image3\\179_soil3.png","image3\\180_soil3.png","image3\\181_soil3.png","image3\\182_soil3.png","image3\\183_soil3.png","image3\\184_soil3.png","image3\\185_soil3.png","image3\\186_soil3.png","image3\\187_soil3.png","image3\\188_soil3.png","image3\\189_soil3.png","image3\\190_soil3.png","image3\\191_soil3.png","image3\\192_soil3.png","image3\\193_soil3.png","image3\\194_soil3.png","image3\\195_soil3.png","image3\\196_soil3.png","image3\\197_soil3.png","image3\\198_soil3.png","image3\\199_soil3.png","image3\\200_soil3.png","image3\\201_soil3.png","image3\\202_soil3.png","image3\\203_soil3.png","image3\\204_soil3.png","image3\\205_soil3.png","image3\\206_soil3.png","image3\\207_soil3.png","image3\\208_soil3.png","image3\\209_soil3.png","image3\\210_soil3.png","image3\\211_soil3.png","image3\\212_soil3.png","image3\\213_soil3.png","image3\\214_soil3.png","image3\\215_soil3.png","image3\\216_soil3.png","image3\\217_soil3.png","image3\\218_soil3.png","image3\\219_soil3.png","image3\\220_soil3.png","image3\\221_soil3.png","image3\\222_soil3.png","image3\\223_soil3.png","image3\\224_soil3.png","image3\\225_soil3.png","image3\\226_soil3.png","image3\\227_soil3.png","image3\\228_soil3.png","image3\\229_soil3.png","image3\\230_soil3.png","image3\\231_soil3.png","image3\\232_soil3.png","image3\\233_soil3.png","image3\\234_soil3.png","image3\\235_soil3.png","image3\\236_soil3.png","image3\\237_soil3.png","image3\\238_soil3.png","image3\\239_soil3.png","image3\\240_soil3.png","image3\\241_soil3.png","image3\\242_soil3.png","image3\\243_soil3.png","image3\\244_soil3.png","image3\\245_soil3.png","image3\\246_soil3.png","image3\\247_soil3.png","image3\\248_soil3.png","image3\\249_soil3.png","image3\\250_soil3.png","image3\\251_soil3.png","image3\\252_soil3.png","image3\\253_soil3.png","image3\\254_soil3.png","image3\\255_soil3.png","image3\\256_soil3.png","image3\\257_soil3.png","image3\\258_soil3.png","image3\\259_soil3.png","image3\\260_soil3.png","image3\\261_soil3.png","image3\\262_soil3.png","image3\\263_soil3.png","image3\\264_soil3.png","image3\\265_soil3.png","image3\\266_soil3.png","image3\\267_soil3.png","image3\\268_soil3.png","image3\\269_soil3.png","image3\\270_soil3.png","image3\\271_soil3.png","image3\\272_soil3.png","image3\\273_soil3.png","image3\\274_soil3.png","image3\\275_soil3.png","image3\\276_soil3.png","image3\\277_soil3.png","image3\\278_soil3.png","image3\\279_soil3.png","image3\\280_soil3.png","image3\\281_soil3.png","image3\\282_soil3.png","image3\\283_soil3.png","image3\\284_soil3.png","image3\\285_soil3.png","image3\\286_soil3.png","image3\\287_soil3.png","image3\\288_soil3.png","image3\\289_soil3.png","image3\\290_soil3.png","image3\\291_soil3.png","image3\\292_soil3.png","image3\\293_soil3.png","image3\\294_soil3.png","image3\\295_soil3.png","image3\\296_soil3.png","image3\\297_soil3.png","image3\\298_soil3.png","image3\\299_soil3.png","image3\\300_soil3.png","image3\\301_soil3.png","image3\\302_soil3.png","image3\\303_soil3.png","image3\\304_soil3.png","image3\\305_soil3.png","image3\\306_soil3.png","image3\\307_soil3.png","image3\\308_soil3.png","image3\\309_soil3.png","image3\\310_soil3.png","image3\\311_soil3.png","image3\\312_soil3.png","image3\\313_soil3.png","image3\\314_soil3.png","image3\\315_soil3.png","image3\\316_soil3.png","image3\\317_soil3.png","image3\\318_soil3.png","image3\\319_soil3.png","image3\\320_soil3.png","image3\\321_soil3.png","image3\\322_soil3.png","image3\\323_soil3.png","image3\\324_soil3.png"};

 int array[13][25];
 soilarray()
 {
	for(int i=0;i<13;i++)
	  for(int j=0;j<25;j++)
	   array[i][j]=1;
 }

void iDraw()
{  
	iClear();
	// iSetColor(255, 0, 0);
	// iFilledRectangle(475, 385, 100, 10);
	if(hmpage==1) homepage(); 
	else if(ins==1) instruction();

	else if(clue==1) cluepage();
	else if(l1==1) level1();
	else if(win==1) winpage();

	else if(clue2==1) cluepage2();
	else if(l2==1) level2();
	else if(win2==1) winpage2();

	else if(clue3==1) cluepage3();
	else if(l3==1) level3();
	else if(win3==1) winpage3();
	

	else if(p1==1 || p2==1 || p3==1) pause();
	else if(over==1) overpage();
}

void homepage()
{   
	hmpage=1; ins=0;
	clue=0; clue2=0; clue3=0;
	l1=0; l2=0; l3=0;
	p1=0; p2=0; p3=0; 
	win=0; win2=0; win3=0;
	life=150;
	x=0; y=0;
	iShowBMP2(0,0,"image\\home.PNG",0);
	iShowBMP2(225,235,"image\\b1.png",0);
	iShowBMP2(225,170,"image\\b2.png",0);
	iShowBMP2(225,105,"image\\b3.png",0);
	soilarray();
    spawn();
} 

void instruction()
{
	hmpage=0; ins=1;
	iShowBMP2(0,0,"image\\ins.png",0);
	iShowBMP2(500,5,"image\\b4.png",0);
}

void cluepage()
{  
	hmpage=0;
	clue=1;
	stand=true;
	iShowBMP2(0,0, "image\\back.png", 0);
	iShowBMP2(10,440,"image\\play.png",0);
	for (int i = 0; i < 43; i++)
	{
	    iShowBMP2(a[i],b[i],snake[sidx],0);
	}
     iShowBMP2(552,0,"image\\box0.png",0);
} 

void level1() {
	iClear();
	hmpage=0;
	//if(c==1) sleep(5);
	//c=0;
    clue=0;
	l1=1;
	p1=0;
	showSoil();
	iShowBMP2(552,0,"image\\box0.png",0);
	iShowBMP2(5,463,"image\\pause.png",0);
    
	if(stand) iShowBMP2(x,y+390,minar[0],0);
    else iShowBMP2(x,y+390,minar[idx],0);
}

void showSoil()
{
	iShowBMP2(0, 390, "image\\backsky.bmp", 0);
	iShowBMP2(0,0, "image\\backsoil2.JPG",0);
	iSetColor(255,0,0);
	iFilledRectangle(440,480,life,8);
	iSetColor(0,0,0);
	iRectangle(440,480,150,8);
	iSetColor(255,0,0);
	iFilledCircle(430,485,10);
	iSetColor(0,0,0);
	iCircle(430,485,10);
	
	
	for (int i = 0; i < 43; i++)
	{
	      iShowBMP2(a[i],b[i],snake[sidx],0);
	}
	
	int k=0;
	for(int i = 0; i < 13; i++)
		for(int j = 0; j < 25; j++)
		{
			
			if(array[i][j] == 1)
				iShowBMP2(j * 24, (12- i) * 30, bi[k], 0);
				k++;
		} 
	k = 0; 
}

void winpage()
{   
	win=1;
	l1=0;
	clue2=0;
	iShowBMP2(0,0,"image\\Level1.png",0);
	life=150; x=0; y=0;
	soilarray();
    spawn();
	
}

void cluepage2()
{  
  
	win=0;
	clue2=1;
	stand=true;
	iShowBMP2(0,0, "image2\\level2.jpg", 0);
	iShowBMP2(10,440,"image\\play.png",0);
	for (int i = 0; i < 43; i++)
	{
	    iShowBMP2(a[i],b[i],snake[sidx],0);
	}
     iShowBMP2(552,0,"image\\box0.png",0);
} 

void level2() {
    clue2=0;
	l2=1;
	p2=0;
	showSoil2();
	iShowBMP2(552,0,"image\\box0.png",0);
	iShowBMP2(5,463,"image\\pause.png",0);
    
	if(stand) iShowBMP2(x,y+390,minar[0],0);
    else iShowBMP2(x,y+390,minar[idx],0);
}

void showSoil2()
{
	iShowBMP2(0, 390, "image2\\sky2.jpg", 0);
	iShowBMP2(0,0, "image\\backsoil2.JPG",0);
	iSetColor(255,0,0);
	iFilledRectangle(440,480,life,8);
	iSetColor(0,0,0);
	iRectangle(440,480,150,8);
	iSetColor(255,0,0);
	iFilledCircle(430,485,10);
	iSetColor(0,0,0);
	iCircle(430,485,10);
	
	
	for (int i = 0; i < 43; i++)
	{
	      iShowBMP2(a[i],b[i],snake[sidx],0);
	}
	
	int k=0;
	for(int i = 0; i < 13; i++)
		for(int j = 0; j < 25; j++)
		{
			
			if(array[i][j] == 1)
				iShowBMP2(j * 24, (12- i) * 30, bib[k],255);
				k++;
		} 
	k = 0; 
} 

void winpage2()
{   
	win2=1;
	l2=0;
	clue3=0;
	iShowBMP2(0,0,"image2\\win2.png",0);
	life=150; x=0; y=0;
	soilarray();
	spawn();
}

void cluepage3()
{  
  
	win2=0;
	clue3=1;
	stand=true;
	iShowBMP2(0,0, "image3\\level3.png", 0);
	iShowBMP2(10,440,"image\\play.png",0);
	for (int i = 0; i < 43; i++)
	{
	    iShowBMP2(a[i],b[i],snake[sidx],0);
	}
     iShowBMP2(552,0,"image\\box0.png",0);
} 

void level3() {
    clue3=0;
	l3=1;
	p3=0;
	showSoil3();
	iShowBMP2(552,0,"image\\box0.png",0);
	iShowBMP2(5,463,"image\\pause.png",0);
    
	if(stand) iShowBMP2(x,y+390,minar[0],0);
    else iShowBMP2(x,y+390,minar[idx],0);
}

void showSoil3()
{
	iShowBMP2(0, 390, "image3\\sky3.png", 0);
	iShowBMP2(0,0, "image\\backsoil.png",0);
	iSetColor(255,0,0);
	iFilledRectangle(440,480,life,8);
	iSetColor(0,0,0);
	iRectangle(440,480,150,8);
	iSetColor(255,0,0);
	iFilledCircle(430,485,10);
	iSetColor(0,0,0);
	iCircle(430,485,10);
	
	
	for (int i = 0; i < 43; i++)
	{
	      iShowBMP2(a[i],b[i],snake[sidx],0);
	}
	
	int k=0;
	for(int i = 0; i < 13; i++)
		for(int j = 0; j < 25; j++)
		{
			
			if(array[i][j] == 1)
				iShowBMP2(j * 24, (12- i) * 30, bic[k],255);
				k++;
		} 
	k = 0; 
} 

void winpage3()
{   
	win3=1;
	l3=0;
	iShowBMP2(0,0,"image3\\win3.png",0);
}
	
void iMouseMove(int mx, int my) {
	//printf("x = %d, y= %d\n",mx,my);
}

void iMouse(int button, int state, int mx, int my) {
	if (button == GLUT_LEFT_BUTTON && state == GLUT_DOWN) {

	    if(hmpage==1&&(mx>=225)&&(mx<=375)&&(my>=235)&&(my<=286)) 
		cluepage();
	    else if(hmpage==1&&(mx>=225)&&(mx<=375)&&(my>=105)&&(my<=156))
	    exit(0);
		else if(hmpage==1&&(mx>=225)&&(mx<=375)&&(my>=170)&&(my<=222))
		instruction();
        else if(ins==1&&(mx>=430)&&(mx<=580)&&(my>=5)&&(my<=67))
		homepage();

		else if(clue==1&&(mx>=10)&&(mx<=106)&&(my>=440)&&(my<=480))
        level1();
		else if(l1==1&&(mx>=5)&&(mx<=40)&&(my>=463)&&(my<=500))
		pause();
		else if(p1==1&&(mx>=30)&&(mx<=180)&&(my>=300)&&(my<=361))
		level1();
		else if(p1==1&&(mx>=30)&&(mx<=180)&&(my>=230)&&(my<=291))
	    homepage();
		else if(p1==1&&(mx>=30)&&(mx<=180)&&(my>=160)&&(my<=221))
		exit(0);
	    else if (win==1) 
	    cluepage2();

        else if(clue2==1&&(mx>=10)&&(mx<=106)&&(my>=440)&&(my<=480))
        level2();
		else if(l2==1&&(mx>=5)&&(mx<=40)&&(my>=463)&&(my<=500))
		pause();
		else if(p2==1&&(mx>=30)&&(mx<=180)&&(my>=300)&&(my<=361))
		level2();
		else if(p2==1&&(mx>=30)&&(mx<=180)&&(my>=230)&&(my<=291))
	    homepage();
		else if(p2==1&&(mx>=30)&&(mx<=180)&&(my>=160)&&(my<=221))
		exit(0);
	    else if (win2==1)
	    cluepage3(); 
        
		else if(clue3==1&&(mx>=10)&&(mx<=106)&&(my>=440)&&(my<=480))
        level3();
		else if(l3==1&&(mx>=5)&&(mx<=40)&&(my>=463)&&(my<=500))
		pause();
		else if(p3==1&&(mx>=30)&&(mx<=180)&&(my>=300)&&(my<=361))
		level3();
		else if(p3==1&&(mx>=30)&&(mx<=180)&&(my>=230)&&(my<=291))
	    homepage();
		else if(p3==1&&(mx>=30)&&(mx<=180)&&(my>=160)&&(my<=221))
		exit(0);
	    else if (win3==1)
	    homepage(); 

 
		else if(over==1)
	    homepage();   
	}
	if (button == GLUT_RIGHT_BUTTON && state == GLUT_DOWN) {
		//place your codes here
		// x -= 10;
		// y -= 10;
	}
}

void iKeyboard(unsigned char key) {
	if (key == 'q')
    {
	 /*	if(musicon)
		{
		   musicon=false;
		   PlaySound(0,0,0);
		}
        else 
		{
			musicon=true;
		} */
    }
	//place your codes for other keys here
	if(key == 'w') 
	{
		y+=30;
		if(y+390>390) y-=30;  // y+390 -> player's initial position.
		                       // y=0 -> inital value of y

		if(idx<3)
		{
			idx++;
			if(idx>=3) idx=0;
		    stand=false;
		}
	    else
		{
			idx++;
		    if(idx>=6) idx=3;
		    stand=false;
		}		
		life-=2;			   
	}
	else if(key == 's') 
	{
		y-=30;
		if(y+390<0) y+=30;

		if(idx<3)
		{
			idx++;
			if(idx>=3) idx=0;
		    stand=false;
		}
	    else
		{
			idx++;
		    if(idx>=6) idx=3;
		    stand=false;
		}
		life-=1;
	}
	else if(key == 'a') 
	{
		x-=24;
		if(x<=-1) x+=24;

		if(idx<3) idx=3;
		idx++;
		if(idx>=6) idx=3;
		stand=false;
		life-=2;
	}
	else if(key == 'd') 
	{
		x+=24;
		if(x>=600) x-=24;

		idx++;
		if(idx>=3) idx=0;
		stand=false;
		life-=1;
	}
}

void iSpecialKeyboard(unsigned char key) {

	if (key == GLUT_KEY_END) {
		exit(0);
	}
}

void pause()
{   
	if(l1==1) { p1=1; l1=0;}
	else if(l2==1) { p2=1; l2=0;}
	else if(l3==1) { p3=1; l3=0;}
	hmpage=0;
    iShowBMP2(0,0,"image\\pause4.png",0);
	iShowBMP2(30,300,"image\\resume.png",0);
	iShowBMP2(30,230,"image\\home2.png",0);
	iShowBMP2(30,160,"image\\close2.png",0);
}
 

void change()
{
	if((y + 390) <= 360 && (y + 390) >=0 && x <= 600 && x >= 0)
		if(array[12 - (y + 390) / 30][x / 24] == 1)
			array[12 - (y + 390) / 30][x / 24] = 0;
	    
}  



void hitpoints()
{
    for(int i=0;i<43;i++)
	{
		if((x==a[i])&&(y+390)==b[i]) 
		{ 
			if(l1==1) life-=50;
			if(l2==1) life-=75;
			if(l3==1) life-=150;
		}
	}

	if(life<=0) overpage();
	else if((x>=552)&&(x<=600)&&(y+390)>=0 && (y+390)<=41) 
    {
		if(l1==1) winpage();
		else if(l2==1) winpage2();
		else if(l3==1) winpage3();
	}

}  

void snakemove()
{
     if(sidx==1) sidx=0;
	 else if(sidx==0) sidx=1;
} 

void overpage()
{
	over=1;
	l1=0; l2=0; l3=0;
	iShowBMP2(0,0,"image\\over2.png",0);
	//iShowBMP2(200,10,"image\\conti.png",0);
} 

int main() {
  srand(time(NULL));
  iSetTimer(500,snakemove);
  iSetTimer(10, change);
  iSetTimer(500,hitpoints);

  if(musicon)
   PlaySound("music\\game.wav",NULL, SND_LOOP | SND_ASYNC );
  iInitialize(600, 500, "GOLD DIGGER");
  return 0;
}
