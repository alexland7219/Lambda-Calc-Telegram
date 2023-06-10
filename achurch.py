from __future__ import annotations
from antlr4 import *
from lcLexer import lcLexer
from lcParser import lcParser
from lcVisitor import lcVisitor
from dataclasses import dataclass
from string import ascii_lowercase as alph
from telegram.ext import *
from telegram import Update
from copy import deepcopy
import pydot

class Buit:
    pass


@dataclass
class Node:
    val: int
    esq: Arbre
    dre: Arbre


Arbre = Node | Buit


def genTreeAbstraction(letters, term):
    if len(letters) == 1:
        return Node("λ", Node(letters[0], Buit(), Buit()), term)
    # else
    return Node("λ", Node(letters[0], Buit(), Buit()), genTreeAbstraction(letters[1:], term))


def getVal(astTree: Node) -> int:
    match astTree:
        case Node(x, izq, dch):
            return x
    raise AssertionError


def printTree(astTree: Arbre) -> str:
    match astTree:
        case Buit():
            return ""
        case Node(x, izq, dch):
            if x == "λ":
                return "(λ" + printTree(izq) + "." + printTree(dch)+")"
            elif x == "@":
                return "(" + printTree(izq) + printTree(dch) + ")"
            else:
                return str(x)


def drawTree(astTree: Arbre, graph, used_nodes, nonfree_vars):
    match astTree:
        case Buit():
            return ("", used_nodes)
        case Node("λ", Node(x, Buit(), Buit()), y):
            mynode = pydot.Node(
                str(used_nodes), label="λ"+x, shape="plaintext")
            graph.add_node(mynode)
            nonfree_vars[x] = mynode
            rightnode, used_nodes = drawTree(
                y, graph, used_nodes+1, nonfree_vars)

            if (rightnode != ""):
                my_right_edge = pydot.Edge(mynode, rightnode)
                graph.add_edge(my_right_edge)

            return (mynode, used_nodes+1)

        case Node(x, izq, dch):
            mynode = pydot.Node(str(used_nodes), label=x, shape="plaintext")
            graph.add_node(mynode)

            leftnode, used_nodes = drawTree(
                izq, graph, used_nodes+1, deepcopy(nonfree_vars))

            rightnode, used_nodes = drawTree(
                dch, graph, used_nodes+1, deepcopy(nonfree_vars))

            if (leftnode == "" and rightnode == ""):
                if x in nonfree_vars.keys():
                    lambdaNode = nonfree_vars[x]
                    extra_edge = pydot.Edge(
                        mynode, lambdaNode, style="dashed", splines="true", color="darkgreen")
                    graph.add_edge(extra_edge)
            elif (leftnode != ""):
                my_left_edge = pydot.Edge(mynode, leftnode)
                graph.add_edge(my_left_edge)
            if (rightnode != ""):
                my_right_edge = pydot.Edge(mynode, rightnode)
                graph.add_edge(my_right_edge)

            return (mynode, used_nodes+1)


def collect_vars(tree: Arbre) -> set:
    match tree:
        case Buit():
            return set()
        case Node(x, y, z):
            if x not in ["@", "λ"]:
                return {x}
            # else
            return collect_vars(y).union(collect_vars(z))


def collect_nonFV(tree: Arbre, banned: str) -> set:
    match tree:
        case Buit():
            return set()
        case Node("λ", Node(p, Buit(), Buit()), q):
            varsOfRight = collect_vars(q)
            if banned in varsOfRight:
                return {p}.union(collect_nonFV(q, banned))
            # else:
            return collect_nonFV(q, banned)
        case Node(x, y, z):
            return collect_nonFV(y, banned).union(collect_nonFV(z, banned))


def conflict(tree1: Arbre, tree2: Arbre, banned: str) -> dict:
    varsTree1 = collect_nonFV(tree1, banned)
    varsTree2 = collect_vars(tree2)
    conf = varsTree1.intersection(varsTree2)

    convert = {}

    if len(conf) == 0:
        return convert  # No alpha reduction needed
    else:
        i = 0
        for x in conf:
            for y in alph[i:]:
                i += 1
                if y not in varsTree1 and y not in varsTree2 and y != banned:
                    convert[x] = y
                    break
            else:
                raise AssertionError(
                    "No free letters left for alpha conversion")

        return convert


def betaReduce(astTree: Arbre, stop=False, bot=False) -> Arbre:
    match astTree:
        case Buit():
            return Buit()
        case Node("@", Node("λ", Node(x, Buit(), Buit()), y), z):
            # Beta reduction
            # Substitute all ocurrences of x in y by z
            #
            # Check if alpha conversion is needed (if y contains z)
            d = conflict(y, z, x)
            for (g, h) in d.items():

                if not bot:
                    print("α-conversion: "+g+" → "+h)
                    print(
                        printTree(Node("λ", Node(x, Buit(), Buit()), y)) + " → ", end="")
                    y = substitute(g, y, Node(h, Buit(), Buit()))
                    print(printTree(Node("λ", Node(x, Buit(), Buit()), y)))
                else:
                    printing_list.append("α-conversió: "+g+" → "+h+"\n")
                    printing_list[-1] += (
                        printTree(Node("λ", Node(x, Buit(), Buit()), y)) + " → ")
                    y = substitute(g, y, Node(h, Buit(), Buit()))
                    printing_list[-1] += printTree(Node("λ",
                                                   Node(x, Buit(), Buit()), y))

            newTree = substitute(x, y, z)

            if not bot:
                print("β-reduction")
                print(printTree(Node(
                    "@", Node("λ", Node(x, Buit(), Buit()), y), z)) + " → " + printTree(newTree))
            else:
                printing_list.append("β-reduction\n")
                printing_list[-1] += (printTree(Node(
                    "@", Node("λ", Node(x, Buit(), Buit()), y), z)) + " → " + printTree(newTree))

            if stop and getVal(newTree) == "λ":
                return newTree
            # else
            return betaReduce(newTree, bot=bot)
        case Node("@", y, z):
            left_tree = betaReduce(y, stop=True, bot=bot)

            match left_tree:
                case Node("λ", Node(x, Buit(), Buit()), t):
                    # Beta reducction
                    #
                    d = conflict(t, z, x)
                    for (g, h) in d.items():
                        if not bot:
                            print("α-conversion: "+g+" → "+h)
                            print(
                                printTree(Node("λ", Node(x, Buit(), Buit()), t)) + " → ", end="")
                            t = substitute(g, t, Node(h, Buit(), Buit()))
                            print(printTree(Node("λ", Node(x, Buit(), Buit()), t)))
                        else:
                            printing_list.append(
                                "α-conversion: "+g+" → "+h+"\n")
                            printing_list[-1] += (
                                printTree(Node("λ", Node(x, Buit(), Buit()), t)) + " → ")
                            t = substitute(g, t, Node(h, Buit(), Buit()))
                            printing_list[-1] += printTree(
                                Node("λ", Node(x, Buit(), Buit()), t))

                    newTree = substitute(x, t, z)

                    if not bot:
                        print("β-reduction")
                        print(printTree(Node(
                            "@", Node("λ", Node(x, Buit(), Buit()), t), z)) + " → " + printTree(newTree))
                    else:
                        printing_list.append("β-reduction\n")
                        printing_list[-1] += (printTree(Node(
                            "@", Node("λ", Node(x, Buit(), Buit()), t), z)) + " → " + printTree(newTree))

                    return betaReduce(newTree, bot=bot)
                case _:
                    return Node("@", left_tree, betaReduce(z, bot=bot))

        case Node(x, y, z):
            return Node(x, betaReduce(y, bot=bot), betaReduce(z, bot=bot))


def substitute(x: str, y: Arbre, z: Arbre) -> Arbre:
    # x is a letter
    # y is a term
    # z is a term
    # returns y, with all ocurrences of x substituted by z
    match y:
        case Buit():
            return Buit()
        case Node(a, b, c):
            if a == x:
                return z
            else:
                return Node(a, substitute(x, b, z), substitute(x, c, z))


class TreeVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by lcParser#root.
    def visitRoot(self, ctx: lcParser.RootContext):
        [term, eof] = list(ctx.getChildren())
        return self.visit(term)

    # Visit a parse tree produced by lcParser#macro.
    def visitMacro(self, ctx: lcParser.MacroContext):
        [name, eq, term] = list(ctx.getChildren())
        return (name.getText(), self.visit(term))

    # Visit a parse tree produced by lcParser#paren.
    def visitParen(self, ctx: lcParser.ParenContext):
        [lparen, term, rparen] = list(ctx.getChildren())
        return self.visit(term)

    # Visit a parse tree produced by lcParser#macroTerm.
    def visitMacroTerm(self, ctx: lcParser.MacroTermContext):
        [name] = list(ctx.getChildren())
        return mdict[name.getText()]

    # Visit a parse tree produced by lcParser#application.
    def visitApplication(self, ctx: lcParser.ApplicationContext):
        [term1, term2] = list(ctx.getChildren())
        term2Text = term2.getText()

        if len(term2Text) == 1 and not term2Text[0].isalpha():
            return Node("@", self.visit(term2), self.visit(term1))
        # else:
        return Node("@", self.visit(term1), self.visit(term2))

    # Visit a parse tree produced by lcParser#letter.
    def visitLetter(self, ctx: lcParser.LetterContext):
        [letter] = list(ctx.getChildren())
        self.visit(letter)
        return Node(letter.getText(), Buit(), Buit())

    # Visit a parse tree produced by lcParser#infix.
    def visitInfix(self, ctx: lcParser.InfixContext):
        [term, op, term2] = list(ctx.getChildren())
        treeOp = mdict[op.getText()]
        return Node("@", Node("@", treeOp, self.visit(term)), self.visit(term2))

    # Visit a parse tree produced by lcParser#abstract.
    def visitAbstract(self, ctx: lcParser.AbstractContext):
        children = list(ctx.getChildren())
        term = self.visit(children[-1])
        letters = []

        for x in children[1:-2]:
            self.visit(x)
            letters.append(x.getText())

        return genTreeAbstraction(letters, term)


mdict = {}          # Llista de macros
printing_list = []  # LLista de string a imprimir

# Do you want to start the Telegram bot or the terminal?
print("\nAChurch - Alexandre Ros i Roger")
while True:
    opt = input(
        "\nDo you want to start the Telegram bot (0) or the command-line version (1) of AChurch? ")
    if opt in {"0", "1"}:
        break


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"λ - COMPUTER!\nWelcome {update.message.chat.first_name}")
    await update.message.reply_text("Use /help for more information on this bot.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    comds = """
            Other helpful commands:
    
/start to Restart this bot
/author to Print the author of this bot
/macro to List the λ-calculus macros registered
/clear to Clear all previous macros registered
    """

    await update.message.reply_text("Welcome to λ - COMPUTER. Insert a λ-calculus expression to begin!")
    await update.message.reply_text(comds)


async def author_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("λ - COMPUTER!\n@ Alexandre Ros Roger, 2023")


def handle_response(text: str) -> list:
    global printing_list

    input_stream = InputStream(text)
    lexer = lcLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = lcParser(token_stream)
    tree = parser.root()

    printing_list = []

    if parser.getNumberOfSyntaxErrors() == 0:
        # print(tree.toStringTree(recog=parser))
        visitor = TreeVisitor()

        if (tree.term()):
            semTree = visitor.visit(tree)
            printing_list.append("Tree\n" + printTree(semTree))
            # Printing the image

            graph = pydot.Dot(
                "my_graph", graph_type="digraph", bgcolor="white")
            _, _ = drawTree(semTree, graph, 0, {})
            graph.write_png("output.png")
            printing_list.append("$iniimage")

            try:
                reducedTree = betaReduce(semTree, bot=True)
                printing_list.append("Result\n")
                printing_list[-1] += printTree(reducedTree)

                graph = pydot.Dot(
                    "my_graph", graph_type="digraph", bgcolor="white")
                _, _ = drawTree(reducedTree, graph, 0, {})
                graph.write_png("output2.png")
                printing_list.append("$finimage")

            except RecursionError:
                printing_list = ["$iniimage"]
                printing_list.append("Result\nNothing")
        else:  # if tree.macro()
            name, semTree = visitor.visit(tree)
            mdict[name] = semTree
            for (key, value) in mdict.items():
                printing_list.append(key + " ≡ " + printTree(value))

        return printing_list
    else:
        printing_list.append(
            "There are syntactical errors with the λ-calculus expression.")

    return printing_list


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    response = handle_response(text)

    print("Bot: ", response)
    for res in response:
        if res == "$iniimage":
            await update.message.reply_photo("output.png")
            continue
        elif res == "$finimage":
            await update.message.reply_photo("output2.png")
            continue
        await update.message.reply_text(res)


async def macro_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global mdict

    # If it's empty
    if not mdict:
        await update.message.reply_text("There are no macros defined.")
    else:
        for key, val in mdict.items():
            await update.message.reply_text(key + " ≡ " + printTree(val))


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global mdict

    mdict = {}
    await update.message.reply_text("All macros erased from memory.")


if opt == "1":
    while True:
        input_stream = InputStream(input('\n? '))
        lexer = lcLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = lcParser(token_stream)
        tree = parser.root()

        if parser.getNumberOfSyntaxErrors() == 0:
            # print(tree.toStringTree(recog=parser))
            visitor = TreeVisitor()

            if (tree.term()):
                semTree = visitor.visit(tree)
                print("Arbre:")
                print(printTree(semTree))
                try:
                    reducedTree = betaReduce(semTree)
                    print("Resultat:")
                    print(printTree(reducedTree))
                except RecursionError:
                    print("Resultat:\nNothing")
            else:  # if tree.macro()
                name, semTree = visitor.visit(tree)
                mdict[name] = semTree
                for (key, value) in mdict.items():
                    print(key + " ≡ " + printTree(value))

        else:
            print(parser.getNumberOfSyntaxErrors(), 'errors de sintaxi.')
            print(tree.toStringTree(recog=parser))
            break

elif opt == "0":

    TOKEN = open("token.txt").read().strip()
    print("\nBot started...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("author", author_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("macro", macro_command))
    app.add_handler(CommandHandler("macros", macro_command))
    app.add_handler(CommandHandler("clear", clear_command))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_error_handler(error)

    app.run_polling(1)
