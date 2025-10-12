# Firestore CLI

This CLI tool allows you to interact with Google Firestore using command-line commands. It includes two main scripts: `fsquery` and `fsupdate`.

## Installation

1. Install from PyPI:

   ```sh
   pip install firestore-cli
   ```

## Usage

### Credentials

To specify the credentials necessary to access Firestore, you can use either of the following methods:

1. Using the `--credentials` option:

   Provide the path to the Firebase credentials JSON file directly via the `--credentials` command-line option.
   Example usage:

   ```
   fsquery --credentials /path/to/your/credentials.json --path your/firestore/collection
   ```

2. Using the `GOOGLE_APPLICATION_CREDENTIALS` environment variable:
   Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of your Firebase credentials JSON file.
   Example usage:
   ```
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json
   fsquery --path your/firestore/collection
   ```

If neither method is provided, the script will attempt to use the default application credentials (which probably won't go well)

### Emulators

If you're using the [local firestore emulators](https://firebase.google.com/docs/emulator-suite/connect_firestore) you'll want to set an environment variable to influence the Firestore SDK. Use whatever port you're running your firestore emulators on. In this example, that port is `8080`.

```shell
export FIRESTORE_EMULATOR_HOST="127.0.0.1:8080"
```

### fsquery

The `fsquery` script allows you to query documents from a Firestore collection.

#### Command Line Options

- `--path collection`: Path to the Firestore collection (required).
- `--credentials`: Path to Firebase credentials JSON file (optional).
- `--database`: Firestore database name (optional, defaults to '(default)').
- `--group`: Specify if this is a collection group query (optional).
- `--where`: Apply multiple filters to the query in the format `field:operation:value` e.g. `--where "some_field == some_value"` (optional). It is recommended to place quotes around the expression.
- `--id`: Query for a specific document ID (optional).
- `--orderby`: Order the results by specified fields, followed by `ASCENDING` or `DESCENDING` (optional).
- `--limit n`: Return *n* or fewer results (optional).
- `--recursion n`: Follow references and fetch the referenced documents up to level *n*, incorporating them into the document that is returned. (optional, default: 0, which does not follow any references.)
- `--out filename`: Write the json output to a file named *filename*

#### Examples

1. **Query all documents in a collection**:

   ```sh
   fsquery --path your-collection
   ```

2. **Query documents with a filter**:

   ```sh
   fsquery --path your-collection --where "field_name == value"
   ```

3. **Write output to a file**

   ```sh
   fsquery --path your-collection --out query.json
   ```

4. **Query documents from a named database**:

   ```sh
   fsquery --path your-collection --database my-database-name
   ```

### fsupdate

The `fsupdate` script allows you to set, add, update, or delete documents in a Firestore collection.

#### Command Line Options

- `--path`: Path to the Firestore collection (required).
- `--credentials`: Path to Firebase credentials JSON file (optional).
- `--database`: Firestore database name (optional, defaults to '(default)').
- `--set`: Set a document with the specified ID.
- `--add`: Add a new document.
- `--update`: Update a document with the specified ID.
- `--delete`: Delete a document with the specified ID.
- `--doc`: Path to the JSON file containing the document data.

#### Examples

1. **Set a document**:

   ```sh
   fsupdate --path your-collection --set your-document-id --doc path/to/your/document.json
   ```

2. **Add a document**:

   ```sh
   fsupdate --path your-collection --add --doc path/to/your/document.json
   ```

3. **Update a document**:

   ```sh
   fsupdate --path your-collection --update your-document-id --doc path/to/your/document.json
   ```

4. **Delete a document**:
   ```sh
   fsupdate --path your-collection --delete your-document-id
   ```

5. **Set a document in a named database**:
   ```sh
   fsupdate --path your-collection --database my-database-name --set your-document-id --doc path/to/your/document.json
   ```

## License

This project is licensed under the MIT License.
