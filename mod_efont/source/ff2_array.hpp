
#pragma once

#include <stdint.h>

#define CAPACITY_STEP_SIZE  128

class ArrayWstr
{
public:
    ArrayWstr()
    {
        data_ = nullptr;
        size_ = 0;
        capacity_ = 0;
    }

    ~ArrayWstr()
    {
        delete[] data_;
    }

    void Append(uint16_t element)
    {
        if (size_ == capacity_)
        {
            capacity_ += 128;
            uint16_t *new_data = new uint16_t[capacity_];
            for (size_t i = 0; i < size_; i++)
            {
                new_data[i] = data_[i];
            }
            delete[] data_;
            data_ = new_data;
        }

        data_[size_] = element;
        size_++;
    }

    size_t Size() const
    {
        return size_;
    }

    template <typename T>
    T operator[](size_t index) const
    {
        if (index < size_)
        {
            return data_[index];
        }
        else
        {
            exit(EXIT_FAILURE);
        }
    }

    operator const wchar_t*() const 
    {
        return (const wchar_t*)data_;
    }

private:
    uint16_t *data_;
    size_t size_;
    size_t capacity_;
};

