import os


def bucket_iterator_json(storage_client, bucket_name):
    if not bucket_exists(storage_client, bucket_name):
        raise ValueError(f'Bucket {bucket_name} does not exist.')
    return storage_client.list_blobs(bucket_name, match_glob="**.json")


def blob_uri_generator(storage_client, bucket_name):
    bucket_iterator = bucket_iterator_json(storage_client, bucket_name)

    blobs = list(bucket_iterator)
    if not blobs:
        raise ValueError(f"There are no blobs in the bucket {bucket_name}.")

    blob_iterator = iter(blobs)
    for blob in blob_iterator:
        blob_name = os.path.splitext(blob.name)[0]
        blob_uri = "gs://" + os.getenv("BUCKET_NAME") + "/" + blob.name
        yield blob_name, blob_uri


def bucket_exists(storage_client, bucket_name):
    bucket = storage_client.bucket(bucket_name)
    return bucket.exists()


def bucket_create(storage_client, bucket_name, location):
    if bucket_exists(storage_client, bucket_name):
        raise ValueError(f"Bucket {bucket_name} already exists.")
    bucket = storage_client.bucket(bucket_name)
    bucket.storage_class = "STANDARD"
    storage_client.create_bucket(bucket, location=location)
    print(f"Created bucket {bucket_name} in {location} with storage class {bucket.storage_class}.")


def blob_exists(storage_client, bucket_name, blob_name):
    if not bucket_exists(storage_client, bucket_name):
        raise ValueError(f'Bucket {bucket_name} does not exist.')

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    return blob.exists()


def delete_blob(storage_client, bucket_name, blob_name):
    if not bucket_exists(storage_client, bucket_name):
        raise ValueError(f'Bucket {bucket_name} does not exist.')

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    if not blob_exists(storage_client, bucket_name, blob_name):
        raise ValueError(f'Blob {blob_name} does not exist in the bucket {bucket_name}.')

    blob.delete()
    print(f"Blob {blob_name} was deleted from the bucket {bucket_name}.")


def extract_blob(storage_client, bucket_name, source_string, destination_blob_name, location):
    if not bucket_exists(storage_client, bucket_name):
        bucket_create(storage_client, bucket_name, location)
    bucket = storage_client.bucket(bucket_name)

    if blob_exists(storage_client, bucket_name, destination_blob_name):
        delete_blob(storage_client, bucket_name, destination_blob_name)

    blob = bucket.blob(destination_blob_name)

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to upload is aborted if the object's
    # generation number does not match your precondition. For a destination
    # object that does not yet exist, set the if_generation_match precondition to 0.
    # If the destination object already exists in your bucket, set instead a
    # generation-match precondition using its generation number.
    generation_match_precondition = 0

    blob.upload_from_string(source_string, if_generation_match=generation_match_precondition)

    print(f"Blob was uploaded to bucket {bucket_name} to the destination {destination_blob_name}.")
