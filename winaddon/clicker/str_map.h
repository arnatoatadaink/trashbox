#include <unordered_map>
using namespace std;

template <class _Tp>  
struct my_equal_to : public binary_function<_Tp, _Tp, bool>  
{  
    bool operator()(const _Tp& __x, const _Tp& __y) const  
    { return strcmp( __x, __y ) == 0; }  
};

struct Hash_Func{
    //BKDR hash algorithm
    int operator()(const char * str)const
    {
        int seed = 131;//31  131 1313 13131131313 etc//
        int hash = 0;
        while(*str)
        {
            hash = (hash * seed) + (*str);
            str ++;
        }

        return hash & (0x7FFFFFFF);
    }
};

template<class _Item>
using str_map = unordered_map<const char*,_Item, Hash_Func,  my_equal_to<const char*> >;
