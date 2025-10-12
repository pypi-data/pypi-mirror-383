// SIDLL

#include "SIDLL.h"

double toDouble(variant<int, double> v) {

    if (std::holds_alternative<double>(v)) {
        return get<double>(v);
    }
    else if (holds_alternative<int>(v)) {
        return static_cast<double>(get<int>(v));
    } 
    else {
        cout << "Error: Unexpected type in variant.\n";
        throw std::runtime_error("Error: Unexpected type in variant.\n");
    }
}

//ListNode class constructor
ListNode::ListNode(int id, double key, variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>> val) :id(id), key(key), val(val), prev(nullptr), next(nullptr) {

}

double ListNode::getKey() {
    return key;
}

int ListNode::getID() {
    return id;
}

variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>>  ListNode::getValue() {
    return val;
}

//NodePointer class constructor
NodePointer::NodePointer(double key = 0, int rightCnt = 0, ListNode* pointer = nullptr) :key(key), rightCnt(rightCnt), pointer(pointer) {
}

void NodePointer::addOne() {
    rightCnt += 1;
}

void NodePointer::removeOne() {
    rightCnt -= 1;
}

void NodePointer::repoint(double newKey, ListNode* newPointer, int rightCnt) {
    key = newKey;
    pointer = newPointer;
    rightCnt = rightCnt;
}

double NodePointer::getKey() {
    return key;
}

int NodePointer::getRightCnt() {
    return rightCnt;
}

void NodePointer::setRightCnt(int val) {
    rightCnt = val;
}

ListNode* NodePointer::getNode() {
    return pointer;
}

int NodePointer::moveToFinal() {
    int cnt = 0;
    if (pointer->next!= nullptr && pointer->next->key == pointer->key) {
        pointer = pointer->next;
        cnt += 1;
        rightCnt -= 1;
    }
    return cnt;
}

SpecialPointer::SpecialPointer(ListNode* listNodePtr):pointer(listNodePtr) {
    key = toDouble(listNodePtr->getKey());
}

void SpecialPointer::moveLeft() {
    if (pointer->prev != nullptr) {
        if (pointer->prev->getKey() > std::numeric_limits<int>::min()) {
            pointer = pointer->prev;
        }
    }
}

void SpecialPointer::moveRight() {
    if (pointer->next != nullptr) {
        pointer = pointer->next;
    }
}

double SpecialPointer::getKey() {
    return key;
}

MedianPointer::MedianPointer(ListNode* listNodePtr):SpecialPointer(listNodePtr) {
}

void MedianPointer::medianMovement(int sidllSize, int mode, double newKey) {
    //Mode: 0: Insert, 1: Delete
    bool even = (sidllSize % 2 == 0) ? 1: 0;

    //Key insertion
    if (mode == 0) {
        if (even) {
            if (newKey < pointer->getKey()) {
                //No movement
            }
            else if (newKey == pointer->getKey()) {
                //No movement
            }
            else {
                moveRight();
            }
            key = toDouble(pointer->getKey());
        }
        else {
            if (newKey < pointer->getKey()) {
                moveLeft();
            }
            else if (newKey == pointer->getKey()) {
                moveLeft();
            }
            else {
                //No movement
            }
            key = (toDouble(pointer->getKey()) + toDouble(pointer->next->getKey())) / 2.0;
        }
    } //Key deletion
    else if (mode == 1 && sidllSize > 1) {
        if (even) {
            if (newKey < pointer->getKey()) {
                moveRight();
            }
            else if (newKey == pointer->getKey()) {
                //Check if there are multiple similar keys
                
                if ((pointer->prev != nullptr && toDouble(pointer->prev->key) == pointer->getKey()) || (pointer->next != nullptr && toDouble(pointer->next->key) == pointer->getKey())) {
                    //No movement
                } 
                 //The listnode pointed to by the medianPointer is deleted  
                
                else {
                    if (pointer->next != nullptr) {
                        moveRight();
                    }
                } 
            }
            else {
                //No movement
            }
            
            //key = toDouble(pointer->getKey());
        }
        else {
            if (newKey < pointer->getKey()) {
                //No movement
            }
            else if (newKey == pointer->getKey()) {
                //It doesn't matter if the medianPointer or other listNodes with similar values are deleted because median has to move left either way.
                moveLeft();
            }
            else {
                moveLeft();
            }
            
            //key = (toDouble(pointer->getKey()) + toDouble(pointer->next->getKey())) / 2.0;
        }
    } 
}

void MedianPointer::medianCorrection(int sidllSize) {
    if (sidllSize > 0) {
        if ((sidllSize) % 2 == 1) {
            moveRight();
        }
        else {
            moveLeft();
        }
    }
}

void MedianPointer::medianRecalc(int sidllSize) {
    bool even = (sidllSize % 2 == 0) ? 1 : 0;

    if (even) {
        key = (toDouble(pointer->getKey()) + toDouble(pointer->next->getKey())) / 2.0;
    }
    else {
        key = toDouble(pointer->getKey());
    }
}

TailPointer::TailPointer(ListNode* listNodePtr): SpecialPointer(listNodePtr) {

}

void TailPointer::checkTail(int mode, double newKey) {
    //Mode: 0: Insert, 1: Delete
    
    //Insert
    if (mode == 0) {
        if (newKey>=key) {
            moveRight();
            key = pointer->getKey();
        }
    }

    //Delete
    else {
        if (key==newKey) {
            moveLeft();
            key = pointer->getKey();
        }
    }
}

//SIDLL class Constructor
SIDLL::SIDLL() {
    headPointer = new ListNode(runningNumber, std::numeric_limits<int>::min(), -1);
    runningNumber += 1;
}

//The main method to insert new pointers
void SIDLL::_insertPointer(double key, ListNode* curr) {
    if (((length / (tree.size() + 1)) >= interpointerDistance) && (tree.count(key) == 0)) {
        if (printVerbosity >= 2) {
            printf("Inserting pointer at %f\n", toDouble(key));
        }
        NodePointer newNP = NodePointer(key, 0, curr);
        tree[key] = newNP;
    }
}

//Check if the requirements are met to insert a new pointer in the middle of another pointer
int SIDLL::_insertPointerInBetween(int currentCnt, ListNode* curr, double key) {

    int tempCnt = 0;
    if ((currentCnt > newPointerthreshold * (interpointerDistance))) {

        ListNode* newCurr = curr;
        while ((newCurr->next != nullptr) && (tempCnt < ((newPointerthreshold / 2) * interpointerDistance))) {
            newCurr = newCurr->next;
            tempCnt += 1;
        }

        if (tree.count(key) == 0) {
            if (printVerbosity >= 2) {
                printf("Inserting pointer at %f\n", newCurr->key);
            }
            
            NodePointer newNP = NodePointer(newCurr->key, currentCnt - tempCnt, newCurr);
            tree[newCurr->key] = newNP;
            
        }
    }
    return tempCnt;
}

//Check if the requirements are met to delete a pointer
int SIDLL::_deletePointerWithCheck(NodePointer* nodePointer, int mode) {
    //Mode: 0 = Force delete, 1 = Normal
    int tempCnt = 0;
    if ((length / (tree.size() + 1)) < (interpointerDistance / 2) || (mode == 0)) {
        if (printVerbosity >= 2) {
            printf("Deleting pointer at %f\n", toDouble(nodePointer->key));
        }

        tempCnt = nodePointer->getRightCnt();
        double key = nodePointer->getKey();
        tree.erase(key);

        //delete &nodePointer;  //<- Testing deleting the NodePointer
    }
    return tempCnt;
}

//Moves a given pointer to one of the neighboring nodes
void SIDLL::_repointPointer(NodePointer nodePointer) {
    int origID = nodePointer.pointer->getID();
    double key = nodePointer.getKey();
    ListNode* curr = nodePointer.getNode();
    ListNode* placeHolder = curr;
    int tempCnt = 0;
    bool conflictFlag = false; //Conflict flag is raised when a pointer is repointed to a value beyond the next pointer or before the previous pointer
    double headKey = headPointer->key;

    auto lb = tree.lower_bound(curr->key);
    if (lb != tree.begin()) {
        --lb;
    }
    while ((curr->prev != nullptr) && (std::abs(tempCnt) < interpointerDistance)) {
        curr = curr->prev;
        tempCnt -= 1;
        if (curr->prev == nullptr || curr->prev->key == headKey) {
            conflictFlag = true;
            break;
        }

        if (curr->prev->getID() != tree[lb->first].pointer->getID()) {
            conflictFlag = false;
            break;
        }
        else if (curr->prev->getID() == tree[lb->first].pointer->getID()) {
            conflictFlag = true;
            break;
        }
    }

    if (conflictFlag == true) {
        auto ub = tree.upper_bound(curr->key);
        if (ub == tree.end()) {
            ub = tree.lower_bound(curr->key);
        }
        while ((curr->next != nullptr) && (tempCnt < interpointerDistance)) {
            curr = curr->next;
            tempCnt += 1;

            if (curr->next == nullptr || curr->next->getID() == tree[ub->first].pointer->getID()) {
                conflictFlag = true;
                break;
            }
            else {
                break;
            }
        }
    }

    /*
    auto ub = tree.upper_bound(curr->key);
    if (ub == tree.end()) {
        ub = tree.lower_bound(curr->key);
    }

    while ((curr->next != nullptr) && (tempCnt < interpointerDistance)) {
        curr = curr->next;
        tempCnt += 1;

        if (curr->next == nullptr || curr->next->getID() == tree[ub->first].pointer->getID()) {
            conflictFlag = true;
            break;
        } 
        else {
            break;
        }
    }

    if (curr->next == nullptr || conflictFlag == true) {
        tempCnt = 0;
        curr = placeHolder;
        double headKey = headPointer->key;
        auto lb = tree.lower_bound(curr->key);
        if (lb != tree.begin()) {
            --lb;
        }
        while ((curr->prev != nullptr) && (std::abs(tempCnt) < interpointerDistance)) {
            curr = curr->prev;
            tempCnt -= 1;
            if (curr->prev == nullptr || curr->prev->key == headKey) {
                conflictFlag = true;
                break;
            }

            if (curr->prev->getID() != tree[lb->first].pointer->getID()) {
                conflictFlag = false;
                break;
            } 
            else if (curr->prev->getID() == tree[lb->first].pointer->getID()) {
                conflictFlag = true;
                break;
            }
        }
    } */

    if (origID == curr->getID()) {
        conflictFlag = true;
    }

    if (conflictFlag) {
        //Delete pointer
        NodePointer* nptr = &nodePointer;
        _deletePointerWithCheck(nptr, 0);
    } else {
        //Repoint
        nodePointer.repoint(curr->key, curr, nodePointer.getRightCnt() + tempCnt);
        if (printVerbosity >= 2) {
            printf("Repointing from: %f (id:%d) to %f (id:%d) \n", toDouble(key), origID, toDouble(curr->key), curr->getID());
        }
        
        if (tree.count(toDouble(key)) != 0) {
            tree.erase(toDouble(key));
            tree[toDouble(curr->key)] = nodePointer;
        }
    }
}



//Finds a pointer for a given key, returns the prev NodePointer object
NodePointer SIDLL::_findPointer(double key)
{
    auto lb = tree.lower_bound(key);
    if (lb != tree.begin()) {
        --lb;
    }
    return lb->second;
}

//Finds a node for a given key starting from a Node Pointer
ListNode* SIDLL::_findNode(double key, NodePointer np, int mode, int relativeIndex=0) {
    
    //Mode: 0: Insert, 1:Delete, 2: Index search
    ListNode* curr = np.pointer;
    int cnt = 0;

    while (curr->next != nullptr) {
        //Insert
        if (mode == 0 && key > curr->next->key) {
            curr = curr->next;
        } //Delete
        else if (mode == 1 && key >= curr->next->key) {
            curr = curr->next;
        }
        else if (mode == 2 && key >= curr->next->key && cnt <= relativeIndex) {
            curr = curr->next;
            if (key == curr->key) {
                cnt += 1;
            }
        }
        else {
            break;
        }
    }

    return curr;
}

//Finds a node starting from head
ListNode* SIDLL::_findNodeFromHead(double key, int mode, int relativeIndex=0) {
    
    //Mode: 0: Insert, 1:Delete, 2: Index search
    ListNode* curr = headPointer;
    int cnt = 0;

    while (curr->next != nullptr) {
        //Insert
        if (mode == 0 && key > curr->next->key) {
            curr = curr->next;
        } //Delete
        else if (mode == 1 && key >= curr->next->key) {
            curr = curr->next;
        }
        else if (mode == 2 && key >= curr->next->key && cnt <= relativeIndex) {
            curr = curr->next;
            if (key == curr->key) {
                cnt += 1;
            }
        }
        else {
            break;
        }
    }

    return curr;
}

//Check if a given key exist
bool SIDLL::keyExists(variant<int, double> origKey) {
    double key = toDouble(origKey);
    ListNode* curr_ = headPointer;

    if (length == 0) {
        return false;
    }

    if (tree.size() == 0) {
        curr_ = _findNodeFromHead(key, 1);
        if (curr_->key == key) {
            return true;
        }
    }
    else {
        if (key <= toDouble(tree.begin()->first)) {
            curr_ = _findNodeFromHead(key, 1);
            if (curr_->key == key) {
                return true;
            }
        }
        else {
            NodePointer np_ = _findPointer(key);
            ListNode* curr_ = _findNode(key, np_, 1);
            if (curr_->key == key) {
                return true;
            }
        }
    }

    return false;
}

//Returns the value for a given key
//If the position is not stated, it will return the first key that matches
variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>> SIDLL::getValue(variant<int, double> origKey, int relativeIndex=0) {
    double key = toDouble(origKey);
    ListNode* curr_ = headPointer;

    if (length == 0) {
        return std::numeric_limits<int>::min();
    } 
    if (tree.size() == 0) {
        curr_ = _findNodeFromHead(key, 2, relativeIndex);
        if (curr_->key == key) {
            return curr_->getValue();
        }
    }
    else {
        if (key <= toDouble(tree.begin()->first)) {
            curr_ = _findNodeFromHead(key, 2, relativeIndex);
            if (curr_->key == key) {
                return curr_->getValue();
            }
        }
        else {
            NodePointer np_ = _findPointer(key);
            ListNode* curr_ = _findNode(key, np_, 2, relativeIndex);
            if (curr_->key == key) {
                return curr_->getValue();
            }
        }
    }

    return std::numeric_limits<int>::min();
}

//Insert helper function
ListNode* SIDLL::_insert(ListNode* curr, double key, variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>> val) {
    
    ListNode* newNode = new ListNode(runningNumber, key, val);
    //length += 1;
    runningNumber += 1;

    newNode->prev = curr;
    newNode->next = curr->next;

    if (curr->next != nullptr) {
        curr->next->prev = newNode;
    }
    curr->next = newNode;
    return newNode;
}

//Inserts a node for a given key, value pair
//Insert could be key only, in which case key == val
void SIDLL::insertNode(variant<int, double> origKey, variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>> val) {
    double key = toDouble(origKey);
    if (printVerbosity >= 1) {
        printf("Inserting %f \n", key);
    }
    ListNode* curr_ = headPointer;

    //If there are currently no nodes 
    if (length == 0) {
        curr_ = _insert(curr_, key, val);
        length += 1;

        mean = (length > 0) ? (((mean * toDouble(length - 1)) + key) / length) : 0;
        medianPointer = new MedianPointer(curr_);
        tailPointer = new TailPointer(curr_);
        //maxKey = max(maxKey, key);
        maxKey = key;
        headRightCnt += 1;
    }
    else {
        //No current nodePointers
        //e.g. Just initialized, no pointers yet
        if (tree.size() == 0) {
            curr_ = _findNodeFromHead(key, 0);
            curr_ = _insert(curr_, key, val);
            medianPointer->medianMovement(getLength(), 0, key);
            tailPointer->checkTail(0, key);
            length += 1;
            mean = (length > 0) ? (((mean * toDouble(length - 1)) + key) / length) : 0;
            
            maxKey = max(maxKey, key);
            headRightCnt += 1;

            _insertPointer(key, curr_);
        }
        //nodePointers exists
        else {
            //Handle the case where the node in question could be before the first pointer
            if (key <= toDouble(tree.begin()->first)) {
                curr_ = _findNodeFromHead(key, 0);
                ListNode* point = _insert(curr_, key, val);
                /*
                if (tree.count(key) != 0) {
                    int addToPrevPointer = tree[key].moveToFinal();
                    headRightCnt += addToPrevPointer;
                } */
                
                medianPointer->medianMovement(getLength(), 0, key);
                tailPointer->checkTail(0, key);
                length += 1;
                mean = (length > 0) ? (((mean * toDouble(length - 1)) + key) / length) : 0;
                
                maxKey = max(maxKey, key);
                headRightCnt += 1;
                int ipc = _insertPointerInBetween(headRightCnt, headPointer, key);
                // If zero is returned, the requirement was not met
                if (ipc != 0) {
                    headRightCnt = ipc;
                }
                else {
                    _insertPointer(key, point);
                }
            }
            else {
                //Use the findPointer to get the relevant pointer
                //Mode 1: Searching for the floor pointer
                NodePointer np_ = _findPointer(key);
                ListNode* curr_ = _findNode(key, np_, 0);
                ListNode* point = _insert(curr_, key, val);
                //If key already has a nodePointer, move the nodePointer to the final in the series of ListNodes
                /*
                if (tree.count(key) != 0) {
                    int addToPrevPointer = tree[key].moveToFinal();
                    tree[np_.key].setRightCnt(np_.getRightCnt() + addToPrevPointer);
                } */
                medianPointer->medianMovement(getLength(), 0, key);
                tailPointer->checkTail(0, key);
                length += 1;
                mean = (length > 0) ? (((mean * toDouble(length - 1)) + key) / length) : 0;
                
                maxKey = max(maxKey, key);
                tree[toDouble(np_.key)].addOne();
                //First check if pointers need to be added nearer to the head
                int ipc = _insertPointerInBetween(headRightCnt, headPointer, key);
                // If zero is returned, the requirement was not met
                if (ipc != 0) {
                    headRightCnt = ipc;
                }
                ipc = _insertPointerInBetween(np_.getRightCnt(), curr_, key);
                // If zero is returned, the requirement was not met
                if (ipc != 0) {
                    tree[toDouble(np_.key)].setRightCnt(ipc);
                }
                else {
                    _insertPointer(key, point);
                }
            }
        }
    }
}

//Delete helper function
ListNode* SIDLL::_delete(ListNode* curr) {
    ListNode* prevNode = curr->prev;
    if (curr->next != nullptr) {
        ListNode* nextNode = curr->next;
        prevNode->next = nextNode;
        nextNode->prev = prevNode;
    }
    else {
        prevNode->next = nullptr;
    }

    //delete curr;
    //Staggered delete: Insert into a deque to be deleted in the next round
    
    
    deleteQ.push_back(curr);
    if (deleteQ.size() > 1) {
        ListNode* toBeDeleted = deleteQ.at(0);
        deleteQ.pop_front();
        delete toBeDeleted;
    }
    
    return prevNode;
}

//Delete a node for a given key
void SIDLL::deleteNode(variant<int, double> origKey) {
    double key = toDouble(origKey);
    if (printVerbosity>=1) {
        printf("Deleting %f\n", key);
    }
    if (length <= 0) {
        return;
    }

    ListNode* curr_ = headPointer;

    //No current nodePointers
    //e.g. Just initialized, no pointers yet
    if (tree.size() == 0) {
        curr_ = _findNodeFromHead(key, 1);
        
        //Reached the exact point to delete

        if (curr_->key == key && length > 0) {  
            deleteBoilerplate(key, curr_);
            /*
            length -= 1;
            if (length == 0) {
                medianPointer = nullptr;
                tailPointer = nullptr;
                ListNode* prev = _delete(curr_);
                maxKey = 0.0;
            }
            else {
                medianPointer->medianMovement(getLength() + 1, 1, key);
                tailPointer->checkTail(1, key);
                if (curr_->getID() == medianPointer->pointer->getID()) {
                    //If there's a conflict, it means that the node key to be deleted is similar to the medianPointer, in that case we move in the opposite direction prior to the actual adjustment
                    medianPointer->medianCorrection(length);
                }
                ListNode* prev = _delete(curr_);
                medianPointer->medianRecalc(length);
                if (key == getMaxKey()) {
                    maxKey = prev->key;
                }
            }
            mean = (length > 0) ? (((mean * toDouble(length + 1)) - key) / length) : 0;
            */
            headRightCnt -= 1;
        }
    }
    //NodePointers are available
    else {
       
        if (key <= tree.begin()->first) {
            curr_ = _findNodeFromHead(key, 1);
            
            if (curr_->key == key) {
                //Check if the current node is a node which is pointed to and repoint node
                if (tree.count(key) > 0) {
                    if (curr_->getID() == tree[key].pointer->getID()) {
                        //if (tree.count(toDouble(curr_->key)) != 0) {
                        NodePointer np_toRepoint = tree[toDouble(curr_->key)];
                        _repointPointer(np_toRepoint);
                    }
                }
                deleteBoilerplate(key, curr_);
                /*
                length -= 1;
                if (length == 0) {
                    medianPointer = nullptr;
                    tailPointer = nullptr;
                    ListNode* prev = _delete(curr_); 
                    maxKey = 0.0;
                }
                else {
                    medianPointer->medianMovement(getLength() + 1, 1, key);
                    tailPointer->checkTail(1, key);
                    if (curr_->getID() == medianPointer->pointer->getID()) {
                        //If there's a conflict, it means that the node key to be deleted is similar to the medianPointer, in that case we move in the opposite direction prior to the actual adjustment
                        medianPointer->medianCorrection(length);
                    }
                    ListNode* prev = _delete(curr_);
                    medianPointer->medianRecalc(length);
                    if (key == getMaxKey()) {
                        maxKey = prev->key;
                    }
                }
                mean = (length > 0) ? (((mean * toDouble(length + 1)) - key) / length) : 0;
                */
                headRightCnt -= 1;

                if (tree.size() > 0) {
                    NodePointer* nodePointerRef = &tree[toDouble(tree.begin()->first)];
                    int ipc = _deletePointerWithCheck(nodePointerRef, 1);
                    // If zero is returned, the requirement was not met
                    if (ipc != 0) {
                        headRightCnt += ipc;
                    }
                }
            }
        }
        else {
            NodePointer np_ = _findPointer(key);
            ListNode* curr_ = _findNode(key, np_, 1);

            if (curr_->key == key) {
                //Check if the current node is a node which is pointed to and repoint node
                if (tree.count(key) > 0) {
                    if (curr_->getID() == tree[key].pointer->getID()) {
                        //if (tree.count(toDouble(curr_->key)) != 0) {
                        NodePointer np_toRepoint = tree.at(toDouble(curr_->key));
                        _repointPointer(np_toRepoint);
                    }
                }
                else {
                    tree[toDouble(np_.key)].removeOne();
                }
                deleteBoilerplate(key, curr_);
                /*
                length -= 1;
                //medianAdjustment(key);
                if (length == 0) {
                    medianPointer = nullptr;
                    tailPointer = nullptr;
                    ListNode* prev = _delete(curr_);
                    maxKey = 0.0;
                }
                else {
                    medianPointer->medianMovement(getLength() + 1, 1, key);
                    tailPointer->checkTail(1, key);
                    if (curr_->getID() == medianPointer->pointer->getID()) {
                        //If there's a conflict, it means that the node key to be deleted is similar to the medianPointer, in that case we move in the opposite direction prior to the actual adjustment
                        medianPointer->medianCorrection(length);
                    }
                    ListNode* prev = _delete(curr_);
                    medianPointer->medianRecalc(length);
                    if (key == getMaxKey()) {
                        maxKey = prev->key;
                    }
                }
                mean = (length > 0) ? (((mean * toDouble(length + 1)) - key) / length) : 0;
                 */
                NodePointer* nodePointerRef = &np_;
                int ipc = _deletePointerWithCheck(nodePointerRef, 1);
                // If zero is returned, the requirement was not met
                if (ipc != 0) {
                    //Find the nodePointer left of the deleted one and add ipc to it
                    double key = np_.key;

                    if (tree.size() > 0) {
                        if (key <= tree.begin()->first) {
                            headRightCnt += ipc;
                        }
                        else if (key >= tree.rbegin()->first) {
                            double ref = tree.rbegin()->first;
                            tree[ref].setRightCnt(tree[ref].getRightCnt() + ipc);
                        }
                        else {
                            auto lb = tree.lower_bound(toDouble(key));
                            --lb;
                            double ref = lb->first;
                            tree[ref].setRightCnt(tree[ref].getRightCnt() + ipc);
                        }
                    } else {
                        headRightCnt += ipc;
                    }                
                }
            }
        }
    }
}

void SIDLL::deleteBoilerplate(double key, ListNode* curr_) {
    length -= 1;
    //medianAdjustment(key);
    if (length == 0) {
        medianPointer = nullptr;
        tailPointer = nullptr;
        ListNode* prev = _delete(curr_);
        maxKey = 0.0;
    }
    else {
        medianPointer->medianMovement(getLength() + 1, 1, key);
        tailPointer->checkTail(1, key);
        if (curr_->getID() == medianPointer->pointer->getID()) {
            //If there's a conflict, it means that the node key to be deleted is similar to the medianPointer, in that case we move in the opposite direction prior to the actual adjustment
            medianPointer->medianCorrection(length);
        }
        ListNode* prev = _delete(curr_);
        medianPointer->medianRecalc(length);
        if (key == getMaxKey()) {
            maxKey = prev->key;
        }
    }
    mean = (length > 0) ? (((mean * toDouble(length + 1)) - key) / length) : 0;
}

//Set the interpointer distance
void SIDLL::setInterpointerDistance(int dist) {
    interpointerDistance = dist;
}

vector <tuple<double, variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>>>> SIDLL::head(int len = 10) {
    vector <tuple<double, variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>>>> res;
    ListNode* curr = headPointer;
    int cnt = 0;
    while (curr->next != nullptr && cnt < len) {
        curr = curr->next;
        res.push_back(make_tuple(curr->getKey(),curr->getValue()));
        cnt += 1;
    }
    return res;
}

vector <tuple<double, variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>>>> SIDLL::tail(int len = 10) {
    vector <tuple<double, variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>>>> res;
    TailPointer* tp = tailPointer;
    if (tp != nullptr) {
        ListNode* curr = tp->pointer;

        double headKey = headPointer->key;
        int cnt = 0;
        //while (curr->prev != nullptr && curr->prev->key != headKey && cnt < len) {
        while (curr->prev != nullptr && curr->key != headKey && cnt < len) {
            res.push_back(make_tuple(curr->getKey(), curr->getValue()));
            curr = curr->prev;
            cnt += 1;
        }
    }
    return res;
}

//Returns the total number of nodes
int SIDLL::getLength() {
    return length;
}

int SIDLL::getTreeSize() {
    return tree.size();
}

double SIDLL::getMaxKey() {
    if (length > 0) {
        return maxKey;
    } else {
        return 0.00;
    }
}

double SIDLL::getMinKey() {
    if (length > 0) {
        return headPointer->next->key;
    } else {
        return 0.00;
    }
    
}

double SIDLL::getMean() {
    return mean;
}

double SIDLL::getMedian() {
    if (medianPointer != nullptr) {
        return medianPointer->getKey();
    }
    return 0.00;
}

void SIDLL::setVerborsity(int mode) {
    printVerbosity = mode;
}

int SIDLL::randomInt(int a, int b) {
    //int rand = a + (std::rand() % (b - a + 1));
    //return rand;

    double randDouble  = randomDouble(a, b);
    return (int) randDouble;
}

double SIDLL::randomDouble(int a, int b) {
    unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
    std::default_random_engine re(seed);

    std::uniform_real_distribution<double> unif(a, b);
    double rand_double = unif(re);

    return rand_double;
}

void SIDLL::getCurrentTime() {
    std::time_t t = std::time(0);
    printf("Current time:%d\n", t);
}

double SIDLL::toDouble(variant<int, double> v) {
    if (std::holds_alternative<double>(v)) {
        return get<double>(v);
    }
    else if (holds_alternative<int>(v)) {
        return static_cast<double>(get<int>(v));
    }
    else {  
        cout << "Error: Unexpected type in variant.\n";
        throw std::runtime_error("Error: Unexpected type in variant.\n");
    }
}

string SIDLL::toString(variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>> v) {
    if (holds_alternative<string>(v)) {
        return get<string>(v);
    }
    else if (holds_alternative<int>(v)) {
        return to_string(get<int>(v));
    }
    else if (holds_alternative<double>(v)) {
        return to_string(get<double>(v));
    }
    else if (holds_alternative<long>(v)) {
        return to_string(get<long>(v));
    }
    else if (holds_alternative<tuple<int, int>>(v)) {
        auto t = get<tuple<int, int>>(v);
        return "[" + to_string(get<0>(t)) + "," + to_string(get<1>(t)) + "]";
    }
    else if (holds_alternative<tuple<int, int, int>>(v)) {
        auto t = get<tuple<int, int, int>>(v);
        return "[" + to_string(get<0>(t)) + "," + to_string(get<1>(t)) + "," + to_string(get<2>(t)) + "]";
    }
    else if (holds_alternative<tuple<double, double>>(v)) {
        auto t = get<tuple<double, double>>(v);
        return "[" + to_string(get<0>(t)) + "," + to_string(get<1>(t)) + "]";
    }
    else if (holds_alternative<tuple<double, double, double>>(v)) {
        auto t = get<tuple<double, double, double>>(v);
        return "[" + to_string(get<0>(t)) + "," + to_string(get<1>(t)) + "," + to_string(get<2>(t)) + "]";
    }
    else if (holds_alternative<tuple<string, string>>(v)) {
        auto t = get<tuple<string, string>>(v);
        return "[" + get<0>(t) + "," + get<1>(t) + "]";
    }
    else if (holds_alternative<tuple<string, string, string>>(v)) {
        auto t = get<tuple<string, string, string>>(v);
        return "[" + get<0>(t) + "," + get<1>(t) + "," + get<2>(t) + "]";
    }
    else {
        cout << "Error: Unexpected type in variant.\n";
        throw std::runtime_error("Error: Unexpected type in variant.\n");
    } 
}

void SIDLL::printOutput() {
    /*
    ("----------------------\n");
    printf("NodePointers:\n");
    int treeSize = tree.size();
    printf("Size: %d\n", treeSize);
    auto a = tree.begin();
    for (int i = 0; i < treeSize; i += 1) {
        printf("Key: %f, ID: %d\n", a->first, a->second.pointer->getID());
        ++a;
    }
    printf("----------------------\n");
    */
    
    /*
    printf("----------------------\n");
    printf("Printing keys:\n");
    ListNode* curr = headPointer;
    double prevVal = curr->key;
    int cnt = 0;
    while (curr->next != nullptr) {
        curr = curr->next;
        printf("%d %f %s\n", curr->getID(), toDouble(curr->key), toString(curr->val).c_str());
        cnt += 1;

        if (curr->next == nullptr) {
            break;
        }

        if (curr->next->key < prevVal) {
            printf("Oops..unordered value detected\n");
        }
        else {
            prevVal = curr->key;
        }
    }
    printf("----------------------\n");
    */

    printf("Length:%d\n", getLength());
    printf("maxKey:%f\n", toDouble(getMaxKey()));
    printf("minKey:%f\n", toDouble(getMinKey()));
    printf("Mean:%f\n", getMean());
    printf("Median:%f\n\n", getMedian());
}

//int main() {
    /*
    ofstream ofs;
    string filename = "siddl_output.txt";
    ofs.open(filename);
    */
    
    /*
    SIDLL s = SIDLL();
    s.setVerborsity(1);
    */
    
    //vector<double> deleteList;
    //vector<variant<int, double, long, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>>> inputList = { string("test"),3.142,100, tuple<int,int>(3,3), tuple<string,string,string>(string("x"),string("y"),string("z"))};
    //int inputListLen = inputList.size() - 1;

    //printf("Inserting...\n");
    //for (int i = 0; i < 100; i += 1) {
        
        /*
        int randInt = s.randomInt(-20, -1);
        s.insertNode(randInt, 0);
        deleteList.push_back(randInt);
        s.printOutput();
        */
        /*
        double rand = s.randomDouble(0, 100);
        //int randInput = s.randomInt(0, inputListLen);
        //s.insertNode(rand, inputList[randInput]);
        s.insertNode(rand, 0);
        deleteList.push_back(rand);
        */
        //s.printOutput();
        //printf("Length:%d\n", s.getLength());
        //printf("Median:%f MP ID: %d\n", s.getMedian(), s.medianPointer->pointer->getID());

        //s.printOutput();
    //}   
    
    /*
    printf("Length:%d\n", s.getLength());
    printf("maxKey:%f\n", s.toDouble(s.getMaxKey()));
    printf("minKey:%f\n", s.toDouble(s.getMinKey()));
    printf("Mean:%f\n", s.getMean());
    printf("Median:%f\n", s.getMedian());
    */

    /*
    for (int i = 0; i < ; i += 1) {
        printf("Length: %d\n",s.length);
        s.deleteNode(s.randomInt(1, 100));
        if (i % 100 == 0) {
            printf("Deleting %d\n",i);
            printf("TreeSize: %d\n", s.getTreeSize());
        }
        //s.printOutput();
        //s.printOutput();
    } */
    
    /*
    printf("Deleting...\n");
    for (int i = 0; i < 100; i += 1) {
        s.deleteNode(deleteList.back());
        deleteList.pop_back();
        s.printOutput();
    }
    
    printf("Length:%d\n", s.getLength());
    printf("maxKey:%f\n", s.toDouble(s.getMaxKey()));
    printf("minKey:%f\n", s.toDouble(s.getMinKey()));
    printf("Mean:%f\n", s.getMean());
    printf("Median:%f\n", s.getMedian());
    
    printf("Reinserting...\n");
    for (int i = 0; i < 100; i += 1) {
        int randInt = s.randomInt(-20, -1);
        s.insertNode(randInt, 0);
        deleteList.push_back(randInt);
        s.printOutput();
        //s.printOutput();
    }
    */
    /*
    printf("No. of nodePointers: %d\n", s.tree.size());
    printf("-----------------------\n");
    printf("Min NodePointer:%f\n", s.tree.begin()->first);
    printf("Max NodePointer:%f\n", s.tree.rbegin()->first);
    printf("\n-----------------------\n");
    */
    //printf("Outputing to file %s...\n", filename.c_str());
    
    /*
    printf("Length:%d\n",s.getLength());
    printf("maxKey:%f\n", s.toDouble(s.getMaxKey()));
    printf("minKey:%f\n", s.toDouble(s.getMinKey()));
    printf("Mean:%f\n", s.getMean());
    printf("Median:%f\n",s.getMedian());
    */
//}
