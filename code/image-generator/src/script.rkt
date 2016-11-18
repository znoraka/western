#lang racket

(require racket/system)


(define params '("--ac" "--dc" "--shuffle" "--xor" "--chrominance" "--luminance"))

(define (to-binary n l)
  (define (binary-with-encoding-length l encoding-length)
    (append (make-list (- encoding-length (length l)) 0) l))

  (binary-with-encoding-length (let div ([n n])
                                 (let ([n n] [rest (modulo n 2)])
                                   (if (equal? (- n rest) 0)
                                       (list rest)
                                       (append (div (/ (- n rest) 2)) (list rest)))))
                               l))
(define (useful? p)
  (and
   (or (= 1 (first p)) (= 1 (second p)))
   (or (= 1 (third p)) (= 1 (fourth p)))
   (or (= 1 (fifth p)) (= 1 (sixth p)))))

(define (create-params)
  (filter-not empty?
              (for/list ([i (range (expt 2 (length params)))])
                (let ([b (to-binary i (length params))])
                  (if (useful? b)
                      (foldl (λ (i j l)
                               (if (= i 1) (cons j l) l)) '() b params)
                      '())))))

(define (create-dataset exec input-path output-path)
  (for-each (λ (i)
              (displayln (~a "executing : " (string-join (append `(,exec ,output-path ,input-path) i))))
              (system (string-join (append `(,exec ,output-path ,input-path) i) " ") #:set-pwd? #t)) (create-params)))

;; (create-dataset "/home/noe/Documents/dev/cdd/code/encryption/bin/crypt" "/home/noe/Downloads/BSR/BSDS500/data/images/train/" "/media/noe/noe/")
