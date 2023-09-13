import sys
import imageio.v2 as iio
import itertools
import numpy
import en_de_cryption as ed

"""
Notes in terms of to do: I want to make the encoding better to spread it over 3 pixels so that the data is much less visible when it's being stored in the image
    So I need to catch the exception of the password being wrong and exit with an incorrect password error. 
    
"""


def convert_text_to_ascii(text):
    text_dec = []
    for character in text:
        text_dec.append(ord(character))
    return text_dec


def convert_ascii_to_text(input_ascii):
    output = ""
    for c in input_ascii:
        output += chr(c)
    return output


def encode_in_image(image, text):
    i = 0
    location = [[]]
    for x, y, z in itertools.product(range(image.shape[0]), range(image.shape[1]), range(image.shape[2])):
        if image[x][y - 1][z] == image[x][y][z] and image[x][y][z] + text[i] <= 255 and i < (len(text) - 1):
            image[x][y][z] += text[i]
            location.append([x, y, z])
            i += 1
        elif image[x][y - 1][z] == image[x][y][z] and image[x][y][z] + text[i] <= 255 and i == (len(text) - 1):
            image[x][y][z] += text[i]
            location.append([x, y, z])
            break
        elif text[i] >= 255:
            i += 1
    return location


def better_encode_in_image(image, text):
    i = 0
    location = [[]]
    for x, y, z in itertools.product(range(image.shape[0]), range(image.shape[1]), range(image.shape[2])):
        if i < (len(text) - 1) and all(image[x][y - 1][t] == image[x][y][t] for t in range(0, 3)):
            if text[i] % 3 == 0 and all((255 - image[x][y - 1][t]) > text[i] / 3 for t in range(0, 3)):
                image[x][y][0] += text[i] / 3
                image[x][y][1] += text[i] / 3
                image[x][y][2] += text[i] / 3
                location.append([x, y])
                i += 1
            elif text[i] % 3 == 1 and all((255 - image[x][y - 1][t]) > (text[i] / 3 + 1) for t in range(0, 3)):
                image[x][y][0] += text[i] / 3
                image[x][y][1] += text[i] / 3
                image[x][y][2] += (1 + text[i] / 3)
                location.append([x, y])
                i += 1
            elif text[i] % 3 == 2 and all((255 - image[x][y - 1][t]) > (text[i] / 3 + 1) for t in range(0, 3)):
                image[x][y][0] += text[i] / 3
                image[x][y][1] += (1 + text[i] / 3)
                image[x][y][2] += (1 + text[i] / 3)
                location.append([x, y])
                i += 1
            elif text[i] >= 255:
                i += 1
    return location


def decode_from_image(data_matrix, encoded_image):
    ascii_out = []
    for j in data_matrix:
        x = int(j[0])
        y = int(j[1])
        ascii_out.append(int(encoded_image[x][y][0]) + int(encoded_image[x][y][1]) + int(encoded_image[x][y][2]) - int(encoded_image[x][y - 1][0]) - int(encoded_image[x][y - 1][1]) - int(encoded_image[x][y - 1][2]))
    return ascii_out


def matrix_to_string(matrix):
    out_array = []
    out_string = ""
    i = 0
    for j in matrix:
        if i > 0:
            out_array.append(j[0])
            out_array.append(j[1])
        i += 1
    for k in out_array:
        out_string += "|" + str(k)
    return out_string


def token_to_location_matrix(input_token):
    input_token = input_token[2:-1]
    try:
        decrypted_string = ed.password_decrypt(input_token.encode(), passwrd).decode()
    except Exception:
        print("Incorrect password, please try again with the  right password.")
        sys.exit(0)
    decrypted_split_string = decrypted_string.split("|")[1:]
    out_array = []
    for i in decrypted_split_string:
        out_array.append(int(i))
    out_location = numpy.asarray(out_array)
    no_of_rows = int(len(out_location) / 2)
    out_matrix = out_location.reshape(no_of_rows, 2)
    return out_matrix


if __name__ == '__main__':
    args = sys.argv[1:]
    mode = args[0].lower()

    if mode == "encode":
        passwrd = args[3]
        image_path = args[1]
        text_path = args[2]

        image_decimal = iio.imread(image_path)
        with open(text_path, 'r') as f:
            text_string = f.read()
        text_decimal = convert_text_to_ascii(text_string)
        encoded_data_location = better_encode_in_image(image_decimal, text_decimal)
        encoded_data_array = matrix_to_string(encoded_data_location)
        encoded_data_array_lock = ed.password_encrypt(encoded_data_array.encode(), passwrd)
        with open("encrypted_key.txt", 'w') as f:
            f.write(str(encoded_data_array_lock))
        iio.imwrite("output_image.png", image_decimal)

    elif mode == "decode":
        passwrd = args[3]
        encoded_image_path = args[1]
        encoded_data_path = args[2]

        encoded_image_decimal = iio.imread(encoded_image_path)
        with open(encoded_data_path, 'r') as f:
            encoded_data_string_lock = f.read()
        encoded_data_matrix = token_to_location_matrix(encoded_data_string_lock)
        output_ascii = decode_from_image(encoded_data_matrix, encoded_image_decimal)
        output_text = convert_ascii_to_text(output_ascii)
        with open("output_text.txt", 'w') as f:
            n = f.write(output_text)
        print(output_text)

    elif mode == "help":
        print("\n"
              "This program encodes a text files into an image please use accordingly.\n"
              "First Parameter: encode, decode, or help\n"
              "Second Parameter: path to the image used for encoding in the case of u-\n"
              "sing the encode option, or path to image to be decoded in a decode opti-\n"
              "on.\n"
              "Third parameter: path to the text file for encoding or path to the file \n"
              "Fourth parameter: password to lock or unlock the encoding location data \n"
              "containing the location of the pixels to be decoded.\n")
    else:
        print("\n"
              "Please enter a valid input parameter. Use help for more details.\n")
