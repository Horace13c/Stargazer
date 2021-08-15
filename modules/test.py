from modules.GANs import gans
import os

if __name__ == '__main__':
    display = """<div id="nn_result">"""

    for file in os.listdir("../model_results/" + "ee7dc67b4df540069f2bf62eaef0faa8"):
        display = display + "<img src='" + "model_results/" + "ee7dc67b4df540069f2bf62eaef0faa8" + "/" + file + "' />"

    display = display + "</div>"

    print(display)