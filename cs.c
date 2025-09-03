#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>
#include <time.h>

sem_t rw_mutex, mutex;
int read_count = 0;
int shared_data = 0;

void* reader(void* arg) {
    long id = (long)arg;
    while (1) {
        printf("Reader %ld: Trying to read...\n", id);
        sem_wait(&mutex);
        read_count++;
        if (read_count == 1)
            sem_wait(&rw_mutex);
        sem_post(&mutex);

        printf("Reader %ld: Reading data: %d\n", id, shared_data);
        sleep(rand() % 2 + 1);

        sem_wait(&mutex);
        read_count--;
        if (read_count == 0)
            sem_post(&rw_mutex);
        sem_post(&mutex);

        printf("Reader %ld: Finished reading.\n", id);
        sleep(rand() % 3 + 2);
    }
    return NULL;
}

void* writer(void* arg) {
    long id = (long)arg;
    while (1) {
        printf("Writer %ld: Trying to write...\n", id);
        sem_wait(&rw_mutex);
        shared_data++;
        printf("Writer %ld: Wrote data: %d\n", id, shared_data);
        sleep(rand() % 3 + 1);

        sem_post(&rw_mutex);
        printf("Writer %ld: Finished writing.\n", id);
        sleep(rand() % 5 + 3);
    }
    return NULL;
}

int main() {
    srand(time(NULL));
    sem_init(&rw_mutex, 0, 1);
    sem_init(&mutex, 0, 1);

    pthread_t r[3], w[2];
    for (long i = 0; i < 3; i++)
        pthread_create(&r[i], NULL, reader, (void*)(i + 1));
    for (long i = 0; i < 2; i++)
        pthread_create(&w[i], NULL, writer, (void*)(i + 1));

    while (1) sleep(10);

    return 0;
}