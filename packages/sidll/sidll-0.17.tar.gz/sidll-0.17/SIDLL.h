#pragma once

#include <deque>
#include <iostream>
#include <cstdio>
#include <stdexcept>
#include <chrono>
#include <variant>
#include <map>
#include <string>
#include <limits>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <random>
#include <vector> 
using namespace std;
using namespace std::chrono;
using std::ofstream;
using std::ios;


class ListNode {
public:
    ListNode(int id, double key, variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>> val);
    double getKey();
    int getID();
    variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>> getValue();

    int id;
    double key;
    variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>> val;
    ListNode* prev;
    ListNode* next;
};

//NodePointer
class NodePointer {
public:
    NodePointer(double key, int rightCnt, ListNode* pointer);

    //Methods
    void addOne(); //rightCnt +1
    void removeOne(); //rightCnt -1
    void repoint(double key, ListNode* pointer, int rightCnt); //repoints pointer to another node
    int moveToFinal();
    double getKey();
    int getRightCnt();
    void setRightCnt(int val);
    ListNode* getNode();

    //Variables
    int rightCnt;
    double key;
    ListNode* pointer;
    //No. of nodes right of the pointer
};

class SpecialPointer {
public:
    SpecialPointer(ListNode* pointer);
    void moveLeft();
    void moveRight();
    double getKey();
    
    double key;
    ListNode* pointer;
};

class MedianPointer : public SpecialPointer {
public:
    MedianPointer(ListNode* pointer);
    
    void medianMovement(int sidllSize, int mode, double newKey);
    void medianCorrection(int sidllSize);
    void medianRecalc(int sidllSize);
};

class TailPointer: public SpecialPointer {
public:
    TailPointer(ListNode* pointer);

    void checkTail(int mode, double newKey);
};

//SIDLL main class
class SIDLL {
public:
    SIDLL();

    //Node methods
    int getLength();
    void insertNode(variant<int, double> key, variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>> val);
    void deleteNode(variant<int, double> key);
    void deleteBoilerplate(double key, ListNode* curr_);
    bool keyExists(variant<int, double> key);
    variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>> getValue(variant<int, double> key, int pos);
    ListNode* _insert(ListNode* curr, double key, variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>> val);
    ListNode* _delete(ListNode* curr); //Returns prev value
    ListNode* _findNode(double key, NodePointer np, int mode, int relativeIndex);
    ListNode* _findNodeFromHead(double key, int mode, int relativeIndex);

    //Pointer methods
    NodePointer _findPointer(double key);
    void _insertPointer(double key, ListNode* curr);
    int _insertPointerInBetween(int currentCnt, ListNode* curr, double currKey);
    int _deletePointerWithCheck(NodePointer* node, int mode);
    void _repointPointer(NodePointer node);
    void getCurrentTime();

    //Other methods
    //float randomFloat(float a,float b);
    void setInterpointerDistance(int dist);

    vector<tuple<double, variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>>>> head(int len);
    vector<tuple<double, variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>>>> tail(int len);
    double getMaxKey();
    double getMinKey();
    double getMean();
    double getMedian();
    int getTreeSize();
    void printOutput();
    //double getTail();
    
    double toDouble(variant<int, double> var);
    string toString(variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple<std::string, std::string, std::string>> var);
    int randomInt(int a, int b);
    double randomDouble(int a, int b);
    void setVerborsity(int mode);
    
    //Variables
    //unordered_map<double, NodePointer> indexDict; //Sparse Indices to LinkNodes: k: key, v: NodePointer object
    //BinarySearchTree bst;
    map<double, NodePointer> tree;

    int length = 0; // Total number of nodes
    int runningNumber = 0;
    int headRightCnt = 0; //No. of nodes before the 1st pointer
    int interpointerDistance = 10; //Default value of distance between 2 pointers
    double maxKey = std::numeric_limits<int>::min(); // Maximum value of the full Linked List
    double minKey = std::numeric_limits<int>::max();
    double mean = 0.0;
    MedianPointer* medianPointer = nullptr;
    TailPointer* tailPointer = nullptr;
    //int nodePointerListMin = std::numeric_limits<int>::max(); // Minimum value of the nodePointerList
    float newPointerthreshold = 1.5; //The distance between 2 pointers beyond which a pointer will be automatically added
    ListNode* headPointer; //Pointer to the first node of the linked list

    deque<ListNode*> deleteQ;
    int printVerbosity=1;
};