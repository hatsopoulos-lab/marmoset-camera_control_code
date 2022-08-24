#include "Spinnaker.h"

#include "SpinGenApi/SpinnakerGenApi.h"

#include <iostream>

#include <sstream> 



#include <sys/types.h>

#include <sys/stat.h>



// for windows mkdir

#ifdef _WIN32

#include <direct.h>

#endif



#include <errno.h>

#include <thread>

#include <vector>

#include <queue>

#include <mutex>

#include <string>

#include <cstring>

#include <dirent.h>



#define HEIGHT 1440

#define WIDTH 1080

#define BYTE_DEPTH 1

#define X_OFFSET 0

#define Y_OFFSET 0



#define RAW_FILE_TYPE "raw"

#define TARGET_FILE_TYPE "jpg"



#define RAW_IMAGE_PIXEL_TYPE PixelFormat_BayerRG8

#define TARGET_IMAGE_FORMAT PixelFormat_BGR8



#define RAW_INPUT_DIR "./cam1"

#define PROCESSED_OUTPUT_DIR "jpg_cam1"







using namespace Spinnaker;

using namespace Spinnaker::GenApi;

using namespace Spinnaker::GenICam;

using namespace std;



std::mutex process_queue_mutex;

std::queue<std::string> raw_image_files;



uint64_t total_files = 0;



bool hasEnding(std::string const &fullString, std::string const &ending) {

	if (fullString.length() >= ending.length()) {

		return (0 == fullString.compare(fullString.length() - ending.length(), ending.length(), ending));

	}

	else {

		return false;

	}

}



void replaceExt(string& s, const string& newExt) {



	string::size_type i = s.rfind('.', s.length());



	if (i != string::npos) {

		s.replace(i + 1, newExt.length(), newExt);

	}

}



int getdir(string dir, queue<string> &files)

{

	DIR *dp;

	struct dirent *dirp;

	if ((dp = opendir(dir.c_str())) == NULL) {

		cout << "Error(" << errno << ") opening " << dir << endl;

		return errno;

	}



	while ((dirp = readdir(dp)) != NULL) {

		if (hasEnding(dirp->d_name, RAW_FILE_TYPE)) {

			files.push(string(dirp->d_name));

		}

	}

	closedir(dp);

	return 0;

}



void processImages(int threadNum) {



		ImagePtr tempImage = Image::Create();

		tempImage->ResetImage(HEIGHT, WIDTH, X_OFFSET, Y_OFFSET, RAW_IMAGE_PIXEL_TYPE);

		unsigned char *buffer = static_cast<unsigned char*>(tempImage->GetData());

		FILE* inFile;



		while (1) {

			process_queue_mutex.lock();

			if (raw_image_files.empty()) {

				process_queue_mutex.unlock();

				return;

			}

			process_queue_mutex.unlock();



			string fileName;

			// get a file to process 

			process_queue_mutex.lock();

			std::cout << "\r                                                                                             \r";

			std::cout << "Files remaining: " << raw_image_files.size() - 1<< "/" << total_files;

			fileName = raw_image_files.front();

			raw_image_files.pop();

			cout << "\t" << " converting file: " << fileName;

			process_queue_mutex.unlock();



			string filepath = string(RAW_INPUT_DIR) + string("/") + fileName;



			inFile = fopen(filepath.c_str(), "rb");



			if (inFile == NULL)

			{

				cout << "Error reading: " << filepath;

				continue;

			}



			fread(buffer, 1, HEIGHT * WIDTH * BYTE_DEPTH, inFile);

			fclose(inFile);



			string newFilename = fileName;

			replaceExt(newFilename, TARGET_FILE_TYPE);



			string newFilepath = string(PROCESSED_OUTPUT_DIR) + string("/") + newFilename;

			try

			{

				ImagePtr convertedImage = tempImage->Convert(TARGET_IMAGE_FORMAT, HQ_LINEAR);

				convertedImage->Save(newFilepath.c_str());

			}

			catch (Spinnaker::Exception &e)

			{

				cout << "Error: " << e.what() << endl;

			}

		}

	

}





// Example entry point; please see Enumeration example for more in-depth 

// comments on preparing and cleaning up the system.

int main(int /*argc*/, char** /*argv*/)

{


	// Since this application saves images in the current folder

	// we must ensure that we have permission to write to this folder.

	// If we do not have permission, fail right away.

	FILE *tempFile = fopen("test.txt", "w+");

	if (tempFile == NULL)

	{

		cout << "Failed to create file in current folder.  Please check "

			"permissions."

			<< endl;

		cout << "Press Enter to exit..." << endl;

		getchar();

		return -1;

	}

	fclose(tempFile);

	remove("test.txt");



	struct stat info;

	stat(PROCESSED_OUTPUT_DIR, &info);



	if (info.st_mode & S_IFDIR) {  // S_ISDIR() doesn't exist on my windows 

		cout << "Output directory exists:  " << PROCESSED_OUTPUT_DIR << endl;

	}

	else

	{ 

		cout << "Creating output directory: " << PROCESSED_OUTPUT_DIR << endl;

		

		int nError = 0;

#if defined(_WIN32)

		nError = _mkdir(PROCESSED_OUTPUT_DIR); // can be used on Windows

#else 

		mode_t nMode = 0733; // UNIX style permissions

		nError = mkdir(PROCESSED_OUTPUT_DIR, nMode); // can be used on non-Windows

#endif

		if (nError != 0) {

			// handle your error here

			cout << "Unable to create directory" << endl;

			cout << endl << endl << "Done! Press Enter to exit..." << endl;

			getchar();

			exit(1);

		}

	}



	// Print application build information

	cout << "Application build date: " << __DATE__ << " " << __TIME__ << endl << endl;



	string dir = string(RAW_INPUT_DIR) + string("/");

	getdir(dir, raw_image_files);

	total_files = raw_image_files.size();

	// unsigned int numThreadsAvailable = std::thread::hardware_concurrency() - 1;

        int numThreadsAvailable = 4;

	std::vector<std::thread> threadTeam;



	for (int i = 0; i < numThreadsAvailable; i++) {

		threadTeam.push_back(std::thread(processImages,i));

	}



	// wait for all threads

	for (auto &e : threadTeam) {

		e.join();

	}



	cout << endl << endl << "Done converting this set - removing raw images and moving to next cam..." << endl;

}

